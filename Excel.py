from concurrent.futures.thread import _WorkItem
import datetime
from email import header
from operator import index
from typing_extensions import deprecated
import xlwings as xw
import pandas as pd

import Conversions as c

def update_excel_by_df(file:str, project: str, data: list[c.RequestProjectItemsResponse]):
    table_data = [
        {
            'Fase do Projeto': item.labels,
            'Referencia': item.number,
            'Atividade': item.title,
            'Status': item.status,
            'Responsável': item.assignee,
            'Atividade Critica': item.priority,
            'Duração': item.estimate,
            'Início': item.start_date,
            'Previsão': item.end_date,
            'Entrega': item.closed_at.strftime("%d/%m/%Y") if item.closed_at is not None else "",
        }
        for item in data
    ]

    df = pd.DataFrame(table_data)

    workbook = xw.Book(file)
    try:
        sheet: xw.Sheet = workbook.sheets[project]
    except:
        workbook.sheets.add(project)
        sheet: xw.Sheet = workbook.sheets[project]
        
    sheet.clear()
    tablename = f"{project}Table"
    sheet.range('A1').options(pd.DataFrame, header=True, index=False).value = df

    n_rows = len(df.index) + 1
    n_cols = len(df.columns)


    data_range = sheet.range((1,1), (n_rows, n_cols))
    try:
        sheet.tables[tablename].delete()
    except:
        pass

    sheet.tables.add(source=data_range , name=tablename)

    sheet.autofit()
    workbook.save()
    workbook.close()


@deprecated('This method is *DEPRECATED* and save item by item, if you want to save a list of items in workbook, use the update_excel_by_df method')
def update_excel(file:str, project: str, data: list[c.RequestProjectItemsResponse]):
    workbook = xw.Book(file)
    sheet: xw.Sheet = workbook.sheets[project]

    references_column = sheet.range("A2").expand('down').value

    if not isinstance(references_column, list):
        references_column = [references_column] if references_column is not None else []

    last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row
    next = last_row + 1

    for item in data:
        if item.number in references_column:
            try:
                ex_row = references_column.index(item.number) + 2
                update_line(sheet, ex_row, item)
            except:
                pass
        else:
            add_line(sheet, next, item)
            references_column.append(item.number)
            next += 1
        sheet.autofit()

    workbook.save()

def update_line(sheet:xw.Sheet, line: int, item: c.RequestProjectItemsResponse):
    sheet.cells(line, 4).value = 0
    sheet.cells(line, 6).value = item.assignee
    if(item.start_date != None):
        sheet.cells(line, 8).value = c.getDateString(item.start_date)
        if(item.estimate != None):
            sheet.cells(line, 9).value = f"{item.start_date.day + item.estimate}/{item.start_date.month}/{item.start_date.year}"
    if(item.end_date != None):
        sheet.cells(line, 10).value = c.getDateString(item.end_date)

def add_line(sheet: xw.Sheet, next_row: int, item: c.RequestProjectItemsResponse):
    sheet.cells(next_row, 1).value = item.labels
    sheet.cells(next_row, 2).value = item.number
    sheet.cells(next_row, 3).value = item.title
    sheet.cells(next_row, 4).value = 0
    sheet.cells(next_row, 5).value = item.priority
    sheet.cells(next_row, 6).value = item.assignee
    sheet.cells(next_row, 7).value = item.status
    if(item.start_date != None):
        sheet.cells(next_row, 8).value = item.start_date
        if(item.estimate != None):
            sheet.cells(next_row, 9).value = f"{item.start_date.day + item.estimate}/{item.start_date.month}/{item.start_date.year}"
            estimate_date = datetime.datetime(
                item.start_date.year, 
                item.start_date.month, 
                item.start_date.day, 
                tzinfo=datetime.timezone.utc
            ) + datetime.timedelta(days=item.estimate)


            sheet.cells(next_row, 11).value = ("Sim" if estimate_date < item.end_date else "Não") if item.end_date is not None else "N/A"


    if(item.end_date != None):
        sheet.cells(next_row, 10).value = item.end_date
    

def find_issue(references, ref: str) -> tuple[bool, int | None]:
    exists = ref in references
    index = None
    if exists:
        index = references.index(ref)
    return exists, index



def verify_if_exists(project):
    print(f'Project: {project['name']}\nNumber: {project['number']}\nPath: {project['sheetPath']}')
    app = xw.App(visible=False)
    book = xw.Book()
    book.sheets.add(project['name'])
    sheet:xw.Sheet = book.sheets[project['name']]
    sheet.cells(1, 1).value = "Fase do Projeto"
    sheet.cells(1, 2).value = "Referencia"
    sheet.cells(1, 3).value = "Atividade"
    sheet.cells(1, 4).value = "Concluido"
    sheet.cells(1, 5).value = "Critica"
    sheet.cells(1, 6).value = "Responsável"
    sheet.cells(1, 7).value = "Status"
    sheet.cells(1, 8).value = "Inicio"
    sheet.cells(1, 9).value = "Previsão"
    sheet.cells(1, 10).value = "Entrega"
    sheet.cells(1, 11).value = "Atraso"
    print(f"Criado a planilha para: {project['name']}")
    book.save(project['sheetPath'])
    book.close()
    app.quit()
    print(f"Arquivo '{project['sheetPath']}' criado para {project['name']} com sucesso!")

