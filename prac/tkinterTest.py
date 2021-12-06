import tkinter.ttk
import asyncio
import random
from common.createTask import createTask

async def main():
    # GUI창을 생성하고 라벨을 설정한다.
    root = tkinter.Tk()
    root.title("Students")
    # root.geometry("540x300+100+100")

    lbl = tkinter.Label(root, text="Class Notice")
    lbl.pack()

    cols = ['sym', 'mark', 'amt', 'diff', 'spread']

    treeview = tkinter.ttk.Treeview(root, columns=cols, show='headings')
    treeview.pack()

    # 각 컬럼 설정. 컬럼 이름, 컬럼 넓이, 정렬 등
    for col in cols:
        treeview.column(col, width=100, anchor="center")
        treeview.heading(col, text=col, anchor="center")

    tasks = []
    tasks.append(createTask(runTkinter(root)))
    tasks.append(createTask(runSomething(treeview)))
    await asyncio.wait(tasks)


def setTreeView(treeview, treelist):
    for i in range(len(treelist)):
        treeview.insert('', i, iid=i)
        # treeview.insert('', i, values=[], iid=i)


def editTreeView(treeview, treelist):
    for i in range(len(treeview.get_children())):
        treeview.item(item=i, values=treelist[i])


def updateTreeView(treeview, treelist):
    lenView = len(treeview.get_children())
    lenData = len(treelist)
    if lenView < lenData:
        for i in range(lenView, lenData):
            treeview.insert('', i, iid=i)
    elif lenView > lenData:
        for i in range(lenData, lenView):
            treeview.delete(i)
    elif lenView == lenData:
        pass
    editTreeView(treeview, treelist)



async def runTkinter(root):
    while True:
        root.update()
        await asyncio.sleep(0.1)


async def runSomething(treeview):
    while True:
        n = random.randint(1, 6)
        treelist = [[n for _ in range(5)] for _ in range(n)]
        updateTreeView(treeview, treelist)
        await asyncio.sleep(1)
        ch = treeview.get_children()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
