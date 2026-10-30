"use client";
// Says so plainly when the demo is replaying recorded responses instead of the live database.
import { useEffect, useState } from "react";
import { isReplay } from "@/lib/api";

export default function ReplayNotice() {
  const [on, setOn] = useState(false);
  useEffect(() => { isReplay().then(setOn); }, []);
  if (!on) return null;
  return (
    <p role="status" className="quote mx-auto mt-4 max-w-[1180px] text-[15px]">
      <span className="label mb-1 block">Recorded run</span>
      The live database is offline, so this demo replays real responses recorded from NODUS. Every plan change
      one save away is included, and what you change stays in this tab.
    </p>
  );
}
