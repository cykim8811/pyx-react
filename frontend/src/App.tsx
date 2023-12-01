import { ReactNode, useMemo } from "react";
import { PyXClient } from "./PyXClient";

export default function App(): ReactNode {
    const client = useMemo(() => new PyXClient(), []);
    if (client) {
        return <div>Client is ready</div>;
    }
    return null;
}

