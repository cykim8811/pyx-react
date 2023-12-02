import { ReactNode } from "react";
import { PyXApp } from "./PyXClient";


export function Renderable({id, app}: {id: string, app: PyXApp}): ReactNode {
    const renderable = app.useRenderable(id);
    return renderable;
}