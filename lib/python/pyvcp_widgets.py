#    This is a component of AXIS, a front-end for emc
#    Copyright 2007 Anders Wallin <anders.wallin@helsinki.fi>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

""" A widget library for pyVCP 
    
    The layoyt and composition of a Python Virtual Control Panel is specified
    with an XML file. The file must begin with <pyvcp>, and end with </pyvcp>

    In the documentation for each widget, optional tags are shown bracketed:
    [ <option>Something</option> ]
    such a tag is not required for pyVCP to work, but may add functionality or
    modify the behaviour of a widget.

    Example XML file:
    <pyvcp>
        <led>
            <size>40</size>
            <halpin>"my-led"</halpin>
        </led>
    </pyvcp>
    This will create a VCP with a single LED widget which indicates the value 
    of HAL pin compname.my-led 
"""

from Tkinter import *
from hal import *
import math

# this makes only functions named here be included in the pydoc
__all__=["pyvcp_label"]


elements =["pyvcp","led","vbox","hbox","vbox" \
            ,"button","scale","checkbutton","bar" \
            ,"label","number","spinbox","radiobutton","jogwheel"]

parameters = ["size","text","orient","halpin","format" \
            ,"font","endval","min_","max_","resolution" \
            ,"from_","to","choices","cpr"]



from Tkinter import *
import math

class pyvcp_jogwheel(Canvas):
    """" A jogwheel that outputs a HAL_FLOAT count
        reacts to both mouse-wheel and mouse dragging
        <jogwheel>
            [ <cpr>33</cpr> ]                       (counts per revolution)
            [ <halpin>"myjogwheel"</halpin> ]
            [ <size>300</size> ]
        </jogwheel>
    """
    # FIXME:
    # -jogging should be enabled only when the circle has focus
    # -circle should maintain focus when mouse over line
    # -jogging by dragging with the mouse could work better
    # -react on arrow keys?
    n=0
    def __init__(self,root,pycomp,halpin=None,size=200,cpr=40,**kw):
        pad=10
        self.count=0
        Canvas.__init__(self,root,width=size,height=size)
        self.circle=self.create_oval(pad,pad,size-pad,size-pad)
        self.itemconfig(self.circle,fill="lightgrey",activefill="darkgrey")
        self.mid=size/2
        self.r=(size-2*pad)/2
        self.alfa=0
        self.d_alfa=2*math.pi/cpr
        self.line = self.create_line([self.mid,self.mid, \
                            self.mid+self.r*math.cos(self.alfa), \
                            self.mid+self.r*math.sin(self.alfa)])
        self.itemconfig(self.line,arrow="last")
        self.itemconfig(self.line,width=3)
        self.bind('<Button-4>',self.wheel_up)
        self.bind('<Button-5>',self.wheel_down)
        self.bind('<Button1-Motion>',self.motion)
        self.bind('<ButtonPress>',self.bdown)
        self.draw_ticks(cpr)
        self.dragstartx=0
        self.dragstarty=0
        self.dragstart=0

        # create the hal pin
        if halpin == None:
            halpin = "jogwheel."+str(pyvcp_jogwheel.n)+".count"
        pyvcp_jogwheel.n += 1
        pycomp.newpin(halpin, HAL_FLOAT, HAL_OUT)
        self.halpin=halpin
        pycomp[self.halpin] = self.count
        self.pycomp=pycomp
    
    def bdown(self,event):
        self.dragstartx=event.x
        self.dragstarty=event.y
        self.dragstart=math.atan2((event.y-self.mid),(event.x-self.mid))

    def motion(self,event):
        dragstop = math.atan2((event.y-self.mid),(event.x-self.mid))
        delta = dragstop - self.dragstart
        if delta>=self.d_alfa:
            self.up()
            self.dragstart=math.atan2((event.y-self.mid),(event.x-self.mid))
        elif delta<=-self.d_alfa:
            self.down()
            self.dragstart=math.atan2((event.y-self.mid),(event.x-self.mid))
    
    def wheel_up(self,event):
        self.up()
        
    def wheel_down(self,event):
        self.down()


    def down(self):
        self.alfa-=self.d_alfa
        self.count-=1
        self.pycomp[self.halpin] = self.count
        self.update_line()       
    
    def up(self):
        self.alfa+=self.d_alfa
        self.count+=1
        self.pycomp[self.halpin] = self.count
        self.update_line()  

    def update_line(self):
        self.coords(self.line, self.mid,self.mid, \
                            self.mid+self.r*math.cos(self.alfa), \
                            self.mid+self.r*math.sin(self.alfa))      

    def draw_ticks(self,cpr):
        for n in range(0,cpr):
            startx=self.mid+self.r*math.cos(n*self.d_alfa)
            starty=self.mid+self.r*math.sin(n*self.d_alfa)
            stopx=self.mid+1.15*self.r*math.cos(n*self.d_alfa)
            stopy=self.mid+1.15*self.r*math.sin(n*self.d_alfa)
            self.create_line([startx,starty,stopx,stopy])

    def update(self,pycomp):
        pass # this is an event drive widget
        




# -------------------------------------------

class pyvcp_radiobutton(Frame):
    n=0
    def __init__(self,master,pycomp,halpin=None,choices=[],**kw):
        f=Frame.__init__(self,master,bd=2,relief=GROOVE)
        self.v = IntVar()
        self.v.set(1)
        self.choices=choices
        if halpin == None:
            halpin = "radiobutton."+str(pyvcp_radiobutton.n)
        pyvcp_radiobutton.n += 1
        
        self.halpins=[]
        n=0
        for c in choices:
            b=Radiobutton(self,f, text=str(c)
                        ,variable=self.v, value=pow(2,n))
            b.pack()
            if n==0:
                b.select()

            c_halpin=halpin+"."+str(c)
            pycomp.newpin(c_halpin, HAL_BIT, HAL_OUT)
            self.halpins.append(c_halpin)
            n+=1

    # FIXME
    # this is a fairly stupid way of updating the pins
    # since the calculation is done every 100ms wether a change
    # has happened or not. see below.   
    def update(self,pycomp):
        index=math.log(self.v.get(),2)
        index=int(index)
        for pin in self.halpins:
            pycomp[pin]=0;
        pycomp[self.halpins[index]]=1;

    # this would be a much better way of updating the
    # pins, but at the moment I can't get it to work
    # this is never called even if I set command=self.update()
    # in the call to Radiobutton above
    def changed(self):
        index=math.log(self.v.get(),2)
        index=int(index)
        print "active:",self.halpins[index]



# -------------------------------------------

class pyvcp_label(Label):
    """ Static text label 
        <label>
            <text>"My Label:"</text>
        </label>
    """
    def __init__(self,master,pycomp,**kw):
        Label.__init__(self,master,**kw)
        
    def update(self,pycomp):
        pass


# -------------------------------------------


class pyvcp_vbox(Frame):
    """ Box in which widgets are packed vertically
        <vbox>
                place widgets here
        </vbox>
    """
    def __init__(self,master,pycomp):
        Frame.__init__(self,master,bd=0,relief=FLAT)
    def update(self,pycomp): 
        pass
    def packtype(self):
        return "top"

# -------------------------------------------

class pyvcp_hbox(Frame):
    """ Box in which widgets are packed horizontally
        <vbox>
                place widgets here
        </vbox>        
    """
    def __init__(self,master,pycomp):
        Frame.__init__(self,master,bd=0,relief=FLAT)
    def update(self,pycomp): 
        pass
    def packtype(self):
        return "left"


# -------------------------------------------


class pyvcp_spinbox(Spinbox):
    """ (control) controls a float, also shown as text 
        reacts to the mouse wheel 
        <spinbox>
            [ <halpin>"my-spinbox"</halpin> ]
            [ <min_>55</min_> ]   sets the minimum value to 55
            [ <max_>123</max_> ]  sets the maximum value to 123
        </spinbox>
    """
    n=0
    def __init__(self,master,pycomp,halpin=None,
                    min_=0,max_=100,resolution=1,format="2.1f",**kw):
        self.v = DoubleVar()
        if 'increment' not in kw: kw['increment'] = resolution
        if 'from' not in kw: kw['from'] = min_
        if 'to' not in kw: kw['to'] = max_
        if 'format' not in kw: kw['format'] = "%" + format
        kw['command'] = self.command
        Spinbox.__init__(self,master,textvariable=self.v,**kw)
        if halpin == None:
            halpin = "spinbox."+str(pyvcp_spinbox.n)
        pyvcp_spinbox.n += 1
        self.halpin=halpin
        self.value=min_
        self.oldvalue=min_
        self.format = "%(b)"+format
        self.max_=max_
        self.min_=min_
        self.resolution=resolution
        self.v.set( str( self.format  % {'b':self.value} ) )
        pycomp.newpin(halpin, HAL_FLOAT, HAL_OUT)
        self.bind('<Button-4>',self.wheel_up)
        self.bind('<Button-5>',self.wheel_down)

    def command(self):
        self.value = self.v.get()

    def update(self,pycomp):  
        pycomp[self.halpin] = self.value 
        if self.value != self.oldvalue:
            self.v.set( str( self.format  % {'b':self.value} ) ) 
            self.oldvalue=self.value
          
    def wheel_up(self,event):
        self.value += self.resolution
        if self.value > self.max_:
            self.value = self.max_
          
     
    def wheel_down(self,event):
        self.value -= self.resolution
        if self.value < self.min_:
            self.value = self.min_
          


# -------------------------------------------

class pyvcp_number(Label):
    """ (indicator) shows a float as text """
    n=0
    def __init__(self,master,pycomp,halpin=None,format="2.1f",**kw):
        self.v = StringVar()
        self.format=format
        Label.__init__(self,master,textvariable=self.v,**kw)
        if halpin == None:
            halpin = "number."+str(pyvcp_number.n)
        pyvcp_number.n += 1
        self.halpin=halpin
        self.value=0.0
        dummy = "%(b)"+self.format
        self.v.set( str( dummy  % {'b':self.value} ) )
        pycomp.newpin(halpin, HAL_FLOAT, HAL_IN)

    def update(self,pycomp):    
        newvalue = pycomp[self.halpin]
        if newvalue != self.value:
            self.value=newvalue
            dummy = "%(b)"+self.format
            self.v.set( str( dummy  % {'b':newvalue} ) )

  

# -------------------------------------------

class pyvcp_bar(Canvas):
    """ (indicator) a bar-indicator for a float"""
    n=0
    def __init__(self,master,pycomp,
              fillcolor="green",bgcolor="grey",
               halpin=None,startval=0.0,endval=100.0,**kw):
        self.cw=200    # canvas width
        self.ch=50     # canvas height
        self.bh=30     # bar height
        self.bw=150    # bar width
        self.pad=((self.cw-self.bw)/2)

        Canvas.__init__(self,master,width=self.cw,height=self.ch)

        if halpin == None:
            halpin = "bar."+str(pyvcp_bar.n)
        pyvcp_bar.n += 1
        self.halpin=halpin
        self.endval=endval
        self.startval=startval
        pycomp.newpin(halpin, HAL_FLOAT, HAL_IN)

        # the border
        border=self.create_rectangle(self.pad,1,self.pad+self.bw,self.bh)
        self.itemconfig(border,fill=bgcolor)

        # the bar
        self.bar=self.create_rectangle(self.pad+1,2,self.pad+1,self.bh-1)
        self.itemconfig(self.bar,fill=fillcolor)
        self.value=0.0 # some dummy value to start with     
          
        # start text
        start_text=self.create_text(self.pad,self.bh+10,text=str(startval) )
        #end text
        end_text=self.create_text(self.pad+self.bw,self.bh+10,text=str(endval) )
        # value text
        self.val_text=self.create_text(self.pad+self.bw/2,
                                   self.bh/2,text=str(self.value) )
          
    def update(self,pycomp):
        # update value
        newvalue=pycomp[self.halpin]
        if newvalue != self.value:
            self.value = newvalue
            percent = self.value/(self.endval-self.startval)
            if percent < 0.0:
                percent = 0
            elif percent > 1.0:
                percent = 1.0  
            # set value text
            valtext = str( "%(b)3.1f" % {'b':self.value} )
            self.itemconfig(self.val_text,text=valtext)
            # set bar size
            self.coords(self.bar, self.pad+1, 2, 
                        self.pad+self.bw*percent, self.bh-1)






# -------------------------------------------




class pyvcp_led(Canvas):
    """ (indicator) a LED 
        color is on_color when halpin is 1, off_color when halpin is 0 """
    n=0
    def __init__(self,master,pycomp, halpin=None,      
                    off_color="red",on_color="green",size=20,**kw):
        Canvas.__init__(self,master,width=size,height=size,bd=0)
        self.off_color=off_color
        self.on_color=on_color
        self.oh=self.create_oval(1,1,size,size)
        self.state=0
        self.itemconfig(self.oh,fill=off_color)
        if halpin == None:
            halpin = "led."+str(pyvcp_led.n)
        
        self.halpin=halpin
        pycomp.newpin(halpin, HAL_BIT, HAL_IN)
        pyvcp_led.n+=1

    def update(self,pycomp):
        newstate = pycomp[self.halpin]
        if newstate != self.state:
            if newstate == 1:
                self.itemconfig(self.oh,fill=self.on_color)
                self.state=1
            else:
                self.itemconfig(self.oh,fill=self.off_color) 
                self.state=0






# -------------------------------------------






class pyvcp_checkbutton(Checkbutton):
    """ (control) a check button 
        halpin is 1 when button checked, 0 otherwise 
    """
    n=0
    def __init__(self,master,pycomp,halpin=None,**kw):
        self.v = BooleanVar(master)
        Checkbutton.__init__(self,master,variable=self.v,onvalue=1, offvalue=0,**kw)
        if halpin == None:
            halpin = "checkbutton."+str(pyvcp_checkbutton.n)
        self.halpin=halpin
        pycomp.newpin(halpin, HAL_BIT, HAL_OUT)
        pyvcp_checkbutton.n += 1

    def update(self,pycomp):
        pycomp[self.halpin]=self.v.get()





# -------------------------------------------






class pyvcp_button(Button):
    """ (control) a button 
        halpin is 1 when button pressed, 0 otherwise 
    """
    n=0
    def __init__(self,master,pycomp,halpin=None,**kw):
        Button.__init__(self,master,**kw)
        if halpin == None:
            halpin = "button."+str(pyvcp_button.n)
        self.halpin=halpin 
        pycomp.newpin(halpin, HAL_BIT, HAL_OUT)
        self.state=0;
        self.bind("<ButtonPress>", self.pressed)
        self.bind("<ButtonRelease>", self.released) 
        pyvcp_button.n += 1    

    def pressed(self,event):
        # "the button was pressed"
        self.state=1     

    def released(self,event):
        # the button was released
        self.state=0

    def update(self,pycomp):
        pycomp[self.halpin]=self.state





# -------------------------------------------




class pyvcp_scale(Scale):
    """ (control) a slider 
        halpin-i is integer output 
        halpin-f is float output 
    """
    n=0
    def __init__(self,master,pycomp,
                    resolution=1,halpin=None,**kw):
        self.resolution=resolution
        Scale.__init__(self,master,resolution=self.resolution,**kw)
        if halpin == None:
            halpin = "scale."+str(pyvcp_scale.n)
        self.halpin=halpin
        
        pycomp.newpin(halpin+"-i", HAL_S32, HAL_OUT)
        pycomp.newpin(halpin+"-f", HAL_FLOAT, HAL_OUT)
        self.bind('<Button-4>',self.wheel_up)
        self.bind('<Button-5>',self.wheel_down)
        pyvcp_scale.n += 1

    def update(self,pycomp):
        pycomp[self.halpin+"-f"]=self.get()
        pycomp[self.halpin+"-i"]=int(self.get())

    def wheel_up(self,event):
        self.set(self.get()+self.resolution)

    def wheel_down(self,event):
        self.set(self.get()-self.resolution)

if __name__ == '__main__':
    print "You can't run pyvcp_widgets.py by itself..."
