from ..cashflow import SinglePaymentFactory as sp
from enum import Enum


class SpreadsheetFeature(Enum):
    NPW = "Net Present Worth"
    CNPW = "Cumulative Net Present Worth"
    # TODO Add more things here (e.g. BCR)


def write_csv(filename, project):
    import csv

    titles = ["Period"] + [cf.get_title() for cf in project.get_cashflows()]
    with open(filename, "w  ", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(titles)

        for n in range(project.periods + 1):
            nextrow = ["n"]
            for cf in project[n]:
                for title in titles:
                    if cf.title == title:  # This can only happen once!
                        nextrow.append(cf[n].amount)
                        break
                    else:
                        nextrow.append(0)
            writer.writerow(nextrow)


def write_excel(filename, project, features=[]):
    import xlsxwriter

    for i, feature in enumerate(features):
        if isinstance(feature, SpreadsheetFeature):
            features[i] = feature.value

    with xlsxwriter.Workbook(filename) as wb:
        bld = wb.add_format({"bold": True})
        pct = wb.add_format({"num_format": "0.00%"})
        fin = wb.add_format(
            {"num_format": '_-$* #,##0.00_-;[Red]-$* #,##0.00_-;_-$* "-"??_-;_-@_-'}
        )

        ws = wb.add_worksheet()

        row, col = 0, 0

        # HEADER
        ws.write(row, 0, project.get_title(), bld)
        row += 1

        ws.write(row, 0, "Interest", bld)
        ws.write(row, 1, project.interest, pct)
        row += 2  # Add space between header and cashflow content

        # TITLES
        cf_titles = [cf.get_title() for cf in project.get_cashflows()]
        print(features)
        titles = ["Period", *cf_titles, *features]
        print(titles)
        ws.write_row(row, 0, titles, bld)
        row += 1

        # PERIODS
        period_col = list(range(project.periods + 1))
        ws.write_column(row, col, period_col)
        col += 1

        # CASHFLOWS
        for cashflow in project.get_cashflows():
            cashflow_list = [cashflow[n].amount for n in range(project.periods + 1)]
            ws.write_column(row, col, cashflow_list, fin)
            col += 1

        # FEATURES
        for feature in features:
            if feature == SpreadsheetFeature.NPW.value:
                npws = [
                    ncf.to_pv(project.interest).amount for ncf in project.get_ncfs()
                ]
                ws.write_column(row, col, npws, fin)
            elif feature == SpreadsheetFeature.CNPW.value:
                npws = [
                    ncf.to_pv(project.interest).amount for ncf in project.get_ncfs()
                ]
                cnpws = npws
                for i in range(1, len(npws)):
                    cnpws[i] += npws[i - 1]
                ws.write_column(row, col, cnpws, fin)

            col += 1
