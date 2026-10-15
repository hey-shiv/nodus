import { Suspense } from "react";
import { DemoNav, Loading } from "@/components/ui";
import PlansClient from "./PlansClient";

export const metadata = { title: "Plans: NODUS live demo" };

export default function PlansPage() {
  return (
    <>
      <DemoNav active="/demo" />
      <Suspense fallback={<Loading what="plans" />}><PlansClient /></Suspense>
    </>
  );
}
