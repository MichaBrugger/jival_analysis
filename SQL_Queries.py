class SQL_Queries:

    SQL_TripHeader = """
        select 
        th_id as 'Trip_Header_ID', 
        convert(smalldatetime,TH_Trip_Date,102) as 'Trip_Date', 
        th_shop_description as 'Shop_Name', 
        th_route_description as 'Route_Name', 
        convert(smalldatetime,first_load_time,108) as 'Trip_StartTime', 
        convert(smalldatetime,driver_completed_datetime,108) as 'Trip_EndTime', 
        TD.[Actual_Delivery], 
        EM_Employee_First_Name + ' ' + EM_Employee_Last_Name 'Driver_Name',
        TL_Join.[Article_Quantity]
        from JL_Trip_Header TH 
        inner join( 
            select tl.TL_Header_ID, 
            sum(tl_quantity) as 'Article_Quantity', 
            TL2.TL_FirstLoad as 'First_Load_Time' 
            from JL_Trip_Load TL 
            inner join(
                select TL_Header_ID, 
                Min(tl_date) as TL_FirstLoad 
                from JL_Trip_Load 
                where TL_Active_Flage = '1' 
                group by TL_Header_ID) TL2 
            on TL.TL_Header_ID = TL2.tl_header_id and tl.TL_Date = tl2.TL_FirstLoad 
            group by tl.TL_Header_ID, tl2.TL_FirstLoad) TL_Join 
        on TH.TH_ID = TL_join.TL_Header_ID 
        inner join(
            select td_trip_header_id, 
            sum(TD_Actual_delivered_qty) as 'Actual_Delivery' 
            from jl_trip_details 
            where TD_Active_Flag = '1' 
            and td_trip_completed = '1' 
            group by td_trip_header_id) TD 
        on TD.TD_Trip_Header_ID = TL_Join.TL_Header_ID 

        inner join jl_employee_master EM
        on TH.TH_Driver_Employee_ID = EM_Employee_ID

        where TH_Trip_Date > DATEADD(day,-14,getdate()) 
            and TH_Active_Flag = '1' 
            and th_route_description not like 'OT Route'
            and ((DATEPART(dw, TH_Trip_Date) + @@DATEFIRST) % 7) NOT IN (1) 
            and IS_RECONCILED = '1' 
            and th_active_flag = '1' 
            and th_route_description != 'OT Route' 
            and IS_DRIVER_COMPLETED = '1' 
            and TH_Trip_Completed = '1'
        """

    SQL_Trip = """
        select
            td_date 'Date',
            TD_Shop_Description 'Shop',
            TD_Route_Description 'Route',
            sum(TD_Planned_Delivery_Qty) 'Planned_Delivery',
            sum(TD_Actual_Delivered_Qty) 'Actual_Delivery',
            EM_Employee_First_Name + ' ' + EM_Employee_Last_Name 'Driver',
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
            and td_date > DATEADD(day,-14,getdate())
        group by TD_Date, TD_Shop_Description, TD_Route_Description, EM_Employee_First_Name + ' ' + EM_Employee_Last_Name
    """

    def get_SQL_TripHeader(self):
        return self.SQL_TripHeader

    def get_SQL_Trip(self):
        return self.SQL_Trip