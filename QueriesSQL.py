class SQL_Queries:
    # Defining all the SQL Queries to be returned in the Main_Analysis

    """
    The SQL_TripHeader query contains information about date and time of a trip, as well as shop, route and driver
    so it can later be merged with other data frames. In detail it contains information from the following tables:
    JL_Trip_Header, JL_Trip_Load and JL_Employee_Master

    JL_Trip_Load is joined with itself to get the min(tl_date) which marks the time the the truck was loaded for the
    in the first time in the morning (usually the truck gets loaded multiple times during a day).
    This can later be compared to the driver_completed_datetime from the JL_Trip_Header table to calculate the total
    time that was needed for a trip.
    The inner join with the JL_Employee_Master makes it possible to match the particular employee who was working on
    that day on that route to the time he needed to complete the trip.
    """

    # Currently, when data for that day is already loaded, daysback has no influence, needs to be changed at some point

    def __init__(self, daysback):

        self.SQL_TripHeader = """
            select 
                convert(smalldatetime,TH_Trip_Date,108) as 'Trip_Date', 
                th_Shop_Description as 'Shop', 
                th_route_description as 'Route', 
                convert(smalldatetime,first_load_time,108) as 'Trip_StartTime', 
                convert(smalldatetime,driver_completed_datetime,108) as 'Trip_EndTime', 
                TH.TH_Driver_Employee_ID as 'Driver_ID'
            from JL_Trip_Header TH 
            
            inner join( 
                select
                tl.TL_Header_ID,
                TL2.TL_FirstLoad as 'First_Load_Time' 
                from JL_Trip_Load TL 
                
                inner join(
                    select
                    TL_Header_ID, 
                    Min(tl_date) as TL_FirstLoad 
                    from JL_Trip_Load 
                    where TL_Active_Flage = '1' 
                    group by TL_Header_ID) TL2 
                on TL.TL_Header_ID = TL2.tl_header_id and tl.TL_Date = tl2.TL_FirstLoad 
                group by tl.TL_Header_ID, tl2.TL_FirstLoad) TL_Join 
            on TH.TH_ID = TL_join.TL_Header_ID
            
            where TH_Trip_Date > DATEADD(day,-{},getdate()) 
                and TH_Active_Flag = '1' 
                and th_route_description not like 'OT Route'
                and ((DATEPART(dw, TH_Trip_Date) + @@DATEFIRST) % 7) NOT IN (1) 
                and IS_RECONCILED = '1' 
                and th_active_flag = '1' 
                and th_route_description != 'OT Route' 
                and IS_DRIVER_COMPLETED = '1' 
                and TH_Trip_Completed = '1'
        """.format(daysback)

        """
        The SQL_Trip query contains information about the actual, planned and zero deliveries that happened on a trip.
        In addition it contains information on shop, route and driver so it can later be merged with other dataframes.
        In detail it contains information from the following tables:
        JL_Trip_Details, JL_Trip_Header and JL_Employee_Master
        
        Zero Deliveries are defined as all deliveries where the planned delivery was bigger than 0 but the actual delivery
        that happened was 0 (which means no delivery happened). 
        """

        self.SQL_Trip = """
            select
                td_date 'Date',
                TD_Shop_Description 'Shop',
                TD_Route_Description 'Route',
                sum(TD_Planned_Delivery_Qty) 'Planned_Delivery',
                sum(TD_Actual_Delivered_Qty) 'Actual_Delivery',
                TH.TH_Driver_Employee_ID 'Driver_ID',
                count(distinct(TD.TD_Customer_ID)) as 'Customer_Count',
                sum(case when (TD_Planned_Delivery_Qty > 0 and TD_Actual_Delivered_Qty = 0) then 1 else 0 end) 'Zero_Delivery'
            from JL_Trip_Details TD
    
            inner join JL_Trip_Header TH
            on TD_Trip_Header_ID = TH.TH_ID
    
            inner join jl_employee_master EM
            on TH.TH_Driver_Employee_ID = EM_Employee_ID
    
            where TD_Active_Flag = '1'
                and td_route_description not like 'OT Route'
                and TD_Trip_Completed = '1'
                and th.TH_Active_Flag = '1'
                and th.TH_Trip_Completed = '1'
                and th.TH_Trip_Status = 'confirmed'
                and ((DATEPART(dw, TD_Date) + @@DATEFIRST) % 7) NOT IN (1) 
                and td_date > DATEADD(day,-{},getdate())
            group by TD_Date, TD_Shop_Description, TD_Route_Description, TH.TH_Driver_Employee_ID
        """.format(daysback)

        """
        The SQL_CustomerAccounts Query contains information about the current total outstanding invoices per route.
        """

        self.SQL_CustomerAccounts = """
            select
                GL_SHOP_DESCRIPTION 'Shop',
                GL_Route_Description 'Route',
                sum(CA_Open_Invoice) as 'Open Invoices'
            from JL_Customer_Accounts
            
            inner join JL_Geo_Location_Master
            on JL_Customer_Accounts.CA_Customer_ID = JL_Geo_Location_Master.GL_Entity_Link
            
            where CA_Default_Flag = '1'
            and CA_Delete_Flag = '0'
            and GL_Default_Flag = '1'
            and GL_Delete_Flag = '0'
            and GL_Entity_Type = 'customer'
            and GL_SHOP_DESCRIPTION is not null
            and GL_Route_Description is not null
            
            group by GL_SHOP_DESCRIPTION, GL_Route_Description
            order by GL_SHOP_DESCRIPTION
        """

        """
        The SQL_CustomerMaster Query provides information on how many new customers a driver acquired in a certain time frame.
        This is accessible since we store the first contact person (CM_Customer_Label) as well as the "joining date"
        (CM_CreationDate) of each customer in our database.
        """

        self.SQL_CustomerMaster = """
            select 
                GL_SHOP_DESCRIPTION 'Shop',
                GL_Route_Description 'Route',
                em.EM_Employee_ID as 'Driver_ID',
                count(distinct(CM_Customer_id)) as 'New Customers'
            from jl_customer_master
    
            left join JL_Geo_Location_Master GL
            on CM_Customer_ID = GL_Entity_Link
    
            left join JL_Employee_Master EM
            on CM_Customer_Label = em.EM_Employee_First_Name + ' ' + em.EM_Employee_Last_Name
    
            where CM_CreationDate > DATEADD(day,-{},getdate())
                and GL_Default_Flag = '1'
                and GL_Delete_Flag = '0'
                and GL_Entity_Type = 'Customer'
                and em.EM_Employee_Status = 'active'
    
            group by GL_SHOP_DESCRIPTION, GL_Route_Description, CM_Customer_Label, em.EM_Employee_ID
        """.format(daysback)

        """
        The SQL_Complaints Query joins the date a complaint was registered for a certain route with the driver that was
        driving this route that day, so it can be seen, how many complaints for each driver on each route were registered.
        """

        self.SQL_Complaints = """
            select
                GL_SHOP_DESCRIPTION 'Shop',
                GL_Route_Description 'Route',
                TH.TH_Driver_Employee_ID 'Driver_ID',
                count(distinct(cm.complaint_number)) as 'Complaints',
                sum(case when cm.IS_CLOSED = 'Y' then 1 else 0 end) as 'Closed Complaints'
            from crm.C_COMPLAINT_MASTER CM
            
            left join JL_Geo_Location_Master GL
            on Cm.CM_CUSTOMER_ID = gl.GL_Entity_Link
            
            left join JL_Trip_Header TH
            on convert(date,cm.CREATED_DATE,101) = convert(date,th.TH_Trip_Date,101) and GL_Route_Description = TH_Route_Description and GL_SHOP_DESCRIPTION = TH_Shop_Description
            
            where GL_Default_Flag = '1'
                and GL_Delete_Flag = '0'
                and GL_Entity_Type = 'customer'
                and GL_Route_Description not like 'inactive%'
                and GL_Route_Description not like 'OT Route'
                and cm.SUB_CATEGORY_ID <> '26'
                and TH_Trip_Completed = '1'
                and TH_Active_Flag = '1'
                and IS_DRIVER_COMPLETED = '1'
                and Cm.CREATED_DATE > DATEADD(day,-{},getdate())
            
            group by gl.GL_SHOP_DESCRIPTION, GL_Route_Description, TH.TH_Driver_Employee_ID
        """.format(daysback)

        """
        The SQL_EmployeeMaster contains information on the names of the drivers that are later matched through the
        Driver_ID, it's important to use the ID for aggregation since there are multiple Drivers with the same name.
        """

        self.SQL_EmployeeMaster = """
            select 
                EM_Employee_ID 'Driver_ID',
                EM_Employee_First_Name + ' ' + EM_Employee_Last_Name 'Driver'
            from JL_Employee_Master
            where EM_employee_type like '%Driver%'
        """

        """
        The SQL_Receipts Query contains information on how much money money was collected in which shop, on which route
        and by which driver.
        """

        self.SQL_Receipts = """
            select
                GL_SHOP_DESCRIPTION as 'Shop',
                GL_Route_Description as 'Route',
                th.TH_Driver_Employee_ID 'Driver_ID',
                sum(BP_Receipt_Amount) as 'Receipts'
            from JL_Receipts
                
            inner join JL_Geo_Location_Master
            on jl_receipts.BP_bill_to_Customer_ID = JL_Geo_Location_Master.GL_Entity_Link
                
            inner join JL_Trip_Header TH
            on GL_Route_Description = TH_Route_Description and GL_SHOP_DESCRIPTION = TH_Shop_Description and convert(date,bp_receipt_date,101) = convert(date,TH_Trip_Date,101)
                
            where BP_Receipt_Date >= '2018-01-01'
                and bp_deleted_flag = '0'
                and GL_Delete_Flag = '0'
                and GL_Entity_Type = 'customer'
                and GL_Default_Flag = '1'
                and gl_route_description not like 'Ot Route'
                and gl_route_description not like 'inactive%'
                and th.TH_Active_Flag = '1'
                and th.TH_Trip_Completed = '1'
                and th.TH_Trip_Status = 'confirmed'
                and IS_RECONCILED = '1'
                and IS_DRIVER_COMPLETED = '1'
                and bp_receipt_date > DATEADD(day,-{},getdate())
            group by GL_SHOP_DESCRIPTION, GL_Route_Description, th.TH_Driver_Employee_ID
        """.format(daysback)

    def get_SQL_TripHeader(self):
        return self.SQL_TripHeader

    def get_SQL_Trip(self):
        return self.SQL_Trip

    def get_SQL_CustomerAccounts(self):
        return self.SQL_CustomerAccounts

    def get_SQL_CustomerMaster(self):
        return self.SQL_CustomerMaster

    def get_SQL_Complaints(self):
        return self.SQL_Complaints

    def get_SQL_EmployeeMaster(self):
        return self.SQL_EmployeeMaster

    def get_SQL_Receipts(self):
        return self.SQL_Receipts