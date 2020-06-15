from ..cashflow import SinglePaymentFactory as sp

def write_csv(filename, project):
    import csv
    
    titles = ["Period"] + [cf.get_title() for cf in project.get_cashflows()]
    with open(filename, 'w  ', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(titles)

        for n in range(project.periods + 1): 
            nextrow = ['n']
            for cf in project[n]:
                for title in titles:
                    if cf.title == title:  # This can only happen once!
                        nextrow.append(cf.cashflow_at(n).amount)
                        break
                    else:
                        nextrow.append(0)
            writer.writerow(nextrow)

def write_excel(filename, project, features=[]):
    import xlsxwriter

    with xlsxwriter.Workbook(filename) as wb:
        bld = wb.add_format({'bold': True})
        pct = wb.add_format({'num_format': '0.00%'})
        fin = wb.add_format({'num_format': '_-$* #,##0.00_-;[Red]-$* #,##0.00_-;_-$* "-"??_-;_-@_-'})

        ws = wb.add_worksheet()
        
        row, col = 0, 0
        
        # HEADER
        ws.write(row, 0, project.title, bld)
        row += 1

        ws.write(row, 0, "Interest", bld)
        ws.write(row, 1, project.interest, pct)
        row += 2  # Add space between header and cashflow content

        # TITLES
        cf_titles = [cf.get_title() for cf in project.get_cashflows()]
        titles = [
            "Period", 
            *cf_titles,
            # *features
        ]
        ws.write_row(row, 0, titles, bld)
        row += 1

        # PERIODS
        period_col = list(range(project.periods + 1))
        ws.write_column(row, col, period_col)
        col += 1

        # CASHFLOWS
        for cashflow in project.get_cashflows():
            cashflow_list = [cashflow.cashflow_at(n).amount for n in range(project.periods + 1)]
            ws.write_column(row, col, cashflow_list, fin)
            col += 1

        # FEATURES - TODO
        # Period NPV
        # Cumulative NPV
        # Period BCR
        # etc...
