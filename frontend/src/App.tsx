import { ReactNode, useMemo } from "react";
import { PyXApp } from "./PyXClient";

export default function App(): ReactNode {
    const app = useMemo(() => new PyXApp(), []);
    const rootID = app.useRootID();
    const root = app.useRenderable(rootID);
    return root;
}

