
import pyx

class Counter:
   def __init__(self):
      self.count = 0
   
   def __render__(self, user):
      async def increment(e):
         print(">", await e.button)
         if (await e.button) == 0:
            self.count += 1
         else:
            self.count -= 1
      
      def contextMenu(e):
         pass
      contextMenu.preventDefault = True
      
      return (
         <div>
            <p>Count: <span style={{'color': 'blue', 'font-weight': 'bold'}}>{self.count}</span></p>
            <button
               onMouseDown={increment}
               onContextMenu={contextMenu}
               >+</button>
         </div>
      )

app = pyx.App(Counter())
app.run()

