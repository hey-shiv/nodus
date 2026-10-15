import { Suspense } from "react";
import { DemoNav, Loading } from "@/components/ui";
import EchoClient from "./EchoClient";

export const metadata = { title: "Echo: NODUS live demo" };

export default function EchoPage() {
  return (
    <>
      <DemoNav active="/demo/echo" />
      <Suspense fallback={<Loading what="the echo" />}><EchoClient /></Suspense>
    </>
  );
}
