import { Suspense } from "react";
import { DemoNav, Loading } from "@/components/ui";
import InboxClient from "./InboxClient";

export const metadata = { title: "Inbox: NODUS live demo" };

export default function InboxPage() {
  return (
    <>
      <DemoNav active="/demo/inbox" />
      <Suspense fallback={<Loading what="the inbox" />}><InboxClient /></Suspense>
    </>
  );
}
