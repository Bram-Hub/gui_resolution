from tkinter import *
from tkinter import ttk

from clause_frame import ClauseFrame

class ResolutionCanvas(Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.frames = dict()    # maps window id to frame
        self.lines = dict()     # maps frame id's to lines between them
        self.touchwidth = 20
        
        self.bind("<Shift-1>", self.add_statement)
        self.bind("<Button-1>", self.click)

    def add_statement(self, event):
        # create the frame
        frame = ClauseFrame(relief="flat", padding=(5, 5))

        # add the frame into the canvas at the click position
        id1 = self.create_window(event.x, event.y, window=frame, tags=("statement"))
        self.frames[id1] = frame
        frame.id = id1

    def click(self, event):
        # 1. get which frame is cicked
        clicked = None     # frame id if clicked
        for frame in self.get_statement_frames():
            c = self.bbox(frame)
            t = self.touchwidth
            if c[0]-t <= event.x <= c[2]+t and c[1]-t <= event.y <= c[3]+t:
                clicked = frame
                break
        
        # 2. see if something is selected
        all_select = self.find_withtag("selected")
        selected = None
        if len(all_select) > 0:
            selected = all_select[0]

        # if so, update the possible parent, etc
        if selected != None:
            if clicked != None:
                # if not the selected frame, update parents stuff
                if clicked != selected:
                    # update the parent
                    other = self.frames[clicked]
                    this = self.frames[selected]
                    
                    if other in this.parents:
                        this.parents.remove(other)
                        other.child = None
                        self.remove_line(clicked, selected)
                    elif len(this.parents) < 2 and other.child == None:
                        this.parents.append(other)
                        other.child = this
                        self.draw_line(clicked, selected)

            # b. if not, deselect the thing
            else:
                self.deselect()     # removes selected tag

        # 3. set the bindings if something is clicked
        if clicked != None and (selected == None or selected == clicked):
            self.bind('<Motion>', self.move_frame)
            self.bind('<ButtonRelease-1>', self.stop)

            # update the clicked to be selected
            self.addtag_withtag('selected', clicked)
            self.frames[clicked].configure(relief="raised")

    def draw_line(self, start, end):
        # get the coordinates
        sbox = self.bbox(start)
        ebox = self.bbox(end)

        x0 = (sbox[0] + sbox[2])*(1/2)
        y0 = sbox[3]

        x1 = (ebox[0] + ebox[2])*(1/2)
        y1 = ebox[1]

        # draw and add the line
        id1 = self.create_line(x0, y0, x1, y1, arrow=LAST)
        self.lines[(start, end)] = id1

    def remove_line(self, start, end):
        if (start, end) in self.lines.keys():
            line = self.lines[(start, end)]
            self.delete(line)
            self.lines.pop((start, end))

    def get_selected(self):
        s = self.find_withtag("selected")
        if len(s) > 0:
            return s[0]
        return None

    def get_statement_frames(self):
        return self.find_withtag("statement")

    # used to drag the clause frames around the screen
    def move_frame(self, event):
        # fetch coordinates
        x, y = event.x, event.y

        # move the frame
        self.coords('selected', x, y)

        # update any lines coming or going
        this = self.get_selected()
        for start, end in self.lines.keys():
            if start == this or end == this:
                self.remove_line(start, end)
                self.draw_line(start, end)

    def stop(self, event):
        self.unbind('<Motion>')

    def deselect(self):
        frames = self.find_withtag("selected")
        for frame in frames:
            self.frames[frame].configure(relief="flat")
        
        self.dtag("selected")
        
        
