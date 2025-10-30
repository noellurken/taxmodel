import pandas as pd

class Box2:
    def __init__(self, initial_equity: float, initial_bonds: float, initial_property: float, 
                 market_return_rate: float, dividend_yield: float, coupon: float, rental_return: float, fee_amount: int, inflation: float, 
                 partners: bool, mtm: bool):
        self.results = []
        self.initial_equity = initial_equity
        self.initial_bonds = initial_bonds
        self.initial_property = initial_property
        self.column_names = [
            'equity_start',         # Column 0
            'bonds_start',          # Column 1
            'property_start',       # Column 2
            'equity_return',        # Column 3
            'dividend_yield',       # Column 4
            'bond_coupon',          # Column 5
            'net_rent',             # Column 6
            'fees',                 # Column 7
            'tax_income',           # Column 8
            'current_tax',          # Column 9
            'cash_account',         # Column 10
            'equity_fv',            # Column 11
            'bonds_fv',             # Column 12
            'property_fv',          # Column 13
            'equity_bv',            # Column 14
            'bonds_bv',             # Column 15
            'property_bv',          # Column 16
            'gain',                 # Column 17
            'deferred_tax',         # Column 18
            'box2_revenue',         # Column 19
            'box2_basis',           # Column 20
            'box2_income',          # Column 21
            'box2_tax',             # Column 22
            'investment_value',     # Column 23
            'exit_tax',             # Column 24
            'net_value',            # Column 25
            ]
        
        self.market_return_rate=market_return_rate
        self.dividend_yield=dividend_yield
        self.coupon=coupon
        self.rental_return=rental_return 
        self.fee_amount=fee_amount
        self.inflation=inflation
        self.partners=partners
        self.mtm=mtm
    
    def get_previous_year_value(self, year: int, column_index: int, default_value: float = 0.0) -> float:
        """
        Get value from previous year for a specific column.
        Returns default_value if it's the first year or column doesn't exist.
        """
        if year == 0:
            return default_value
        return self.results[year - 1][column_index]
    
    def calculate_year(self, year,
                        vpbRate_slice1=0.19, vpbRate_slice2=0.258, vpb_slices_at=200000, 
                        box2Rate_slice1=0.245, box2Rate_slice2=0.31, box2_slices_at=67000):
        
        """Calculate all values for a given year, with references to previous year's data."""
        
        # Initialize row
        row = [0] * len(self.column_names)
        

        # Columns 0, 1, 2: Start values 
        row[0] = self.initial_equity if year == 0 else self.get_previous_year_value(year,11)  # 11 is equity_fv
        print(row[0], self.market_return_rate)
        
        row[1] = self.initial_bonds if year == 0 else self.get_previous_year_value(year, 12)  # 12 is bonds_fv
        row[2] = self.initial_property if year == 0 else self.get_previous_year_value(year, 13)  # 13 is property_fv
        
        # Columns 3, 4, 5, 6: Market return calculations
        row[3] = float(row[0] * self.market_return_rate)
        row[4] = float(row[0] * self.dividend_yield)
        row[5] = float(row[1] * self.coupon)
        row[6] = float(row[2] * self.rental_return)
        
        # Column 7: Fee
        row[7] = float(self.fee_amount)

        # Column 8, 9: taxable income and current tax expense
        if self.mtm is True:
            row[8] = row[3]+row[4]+row[5]+row[6]-row[7]
        else:
            row[8] = row[4]+row[5]+row[6]-row[7]

        if row[8] > vpb_slices_at:
            row[9] = (row[8] - vpb_slices_at) * vpbRate_slice2 + (vpbRate_slice1 * vpb_slices_at)
        else:
            row[9] = row[8] * vpbRate_slice1

        # Column 10: cash account
        prior_cash_balance = 0 if year == 0 else self.get_previous_year_value(year, 10)  # 10 is cash_account
        row[10] = row[4]+row[5]+row[6]-row[7]-row[9] + prior_cash_balance
        
        # Column 11, 12, 13: Fair value of investments
        row[11] = row[0] + row [3]
        row[12] = row[1]
        row[13] = row[2] * (1+self.inflation)

        # Column 14, 15, 16: Book value of investments
        row[14] = row[11] if self.mtm == True else self.initial_equity
        row[15] = self.initial_bonds
        row[16] = self.initial_property
        
        # Column 17, 18: Deferred gain and tax
        row[17] = (row[11]+row[12]+row[13]) - (row[14]+row[15]+row[16]) ## Fair value minus cost price = gain

        if row[17] > vpb_slices_at:
            row[18] = row[17] * vpbRate_slice2
        
        elif (row[8]+row[17]) < vpb_slices_at:
            row[18] = row[17] * vpbRate_slice1

        else:
            residual_slice = vpb_slices_at - row[8]
            row[18] = residual_slice * vpbRate_slice1 + (row[17] - residual_slice) * vpbRate_slice2
        
        # Column 19, 20, 21, 22: Box 2 values and tax
        row[19] = row[11]+row[12]+row[13]+row[10] - row[18]
        row[20] = self.initial_equity+self.initial_bonds+self.initial_property
        row[21] = row[19] - row[20]
          
        if self.partners == True:
            
            if row[21] > (2 * box2_slices_at):
                row[22] = (row[21] - (2 * box2_slices_at)) * box2Rate_slice2 + (2 * box2_slices_at * box2Rate_slice1)
            
            else:
                row[22] = row[21] * box2Rate_slice1

        else:
            
            if row[21] > box2_slices_at:
                row[22] = (row[21] - box2_slices_at) * box2Rate_slice2 + box2_slices_at * box2Rate_slice1
            
            else:
                row[22] = row[21] * box2Rate_slice1

        # Columns 23, 24, 25, 25: Metrics
        row[23] = row[10]+row[11]+row[12]+row[13]   ## investment value
        row[24] = row[22]                           ## exit tax
        row[25] = row[23]-row[24]                   ## net
        
        self.results.append(row)
        return row
    
    def run_model(self, years):
        """Run the model for specified number of years."""
        for year in range(years):
            self.calculate_year(year)
        
        results = self.results
        df = pd.DataFrame(results, columns=self.column_names).astype('int')

        return df

    def chart_data(self, years):
        data = self.run_model(years)

        df = data[['investment_value', 'exit_tax', 'net_value']]

        return df

'''
bram_spaarpot = Box2(initial_equity=10000, initial_bonds=10000, initial_property=0,
                market_return_rate=0.06,
                dividend_yield=0.02,
                coupon=0.035,
                rental_return=0.065,
                fee_amount=25,
                inflation=0.02,
                partners=True,
                mtm=True)

print(bram_spaarpot.chart_data(50))

'''
