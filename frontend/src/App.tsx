
// import { createElement } from "react";
import { useEffect } from "react";
import { socket } from "./socket";

function App() {

  useEffect(() => {
    socket.on('connect', () => {
      console.log('Connected to server');
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from server');
    });

    socket.on('message', (data: any) => {
      console.log(data);
    });

    return () => {
      socket.off('connect');
      socket.off('disconnect');
      socket.off('message');
    }
  }, []);

  return (
    <>
      <div>
        <h1>PyX React</h1>
      </div>
    </>
  )
}

export default App;
