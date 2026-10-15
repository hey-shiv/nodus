import { Suspense } from "react";
import { DemoNav, Loading } from "@/components/ui";
import LessonsClient from "./LessonsClient";

export const metadata = { title: "Lessons: NODUS live demo" };

export default function LessonsPage() {
  return (
    <>
      <DemoNav active="/demo/lessons" />
      <Suspense fallback={<Loading what="lessons" />}><LessonsClient /></Suspense>
    </>
  );
}
