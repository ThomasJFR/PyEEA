from ..cashflow import SinglePaymentFactory as sp

def to_csv(filename, project):
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

def to_excel(filename, project, show_npv=False):
    import xlsxwriter

    titles = ["Period"] + [cf.get_title() for cf in project.get_cashflows()]
    with xlsxwriter.Workbook(filename) as wb:
        ws = wb.add_worksheet()
        bld = wb.add_format({'bold': True})
        fin = wb.add_format({'num_format': '_-$* #,##0.00_-;[Red]-$* #,##0.00_-;_-$* "-"??_-;_-@_-'})
        
        # TITLES
        for i in range(len(titles)):
            ws.write(0, i, titles[i], bld)
        if show_npv:
            ws.write(0, len(titles), "Net Present Worth", bld)

        # DATA
        row = 1
        for n in range(project.periods + 1): 
            ws.write(row, 0, n)
            for cf in project[n]:
                for col, title in enumerate(titles):
                    if cf.title == title:  # This can only happen once!
                        ws.write(row, col, cf.cashflow_at(n).amount, fin)
            if show_npv:
                npv = sum([cf @ n for cf in project[n]]).to_pv(project.interest).amount
                ws.write(row, len(titles), npv, fin)
            row += 1

