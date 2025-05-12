import React, { useEffect, useRef } from "react";
import BpmnJS from "bpmn-js";

interface BpmnEditorProps {
  xml: string;
}

const BpmnEditor: React.FC<BpmnEditorProps> = ({ xml }) => {
  const ref = useRef<HTMLDivElement>(null);
  const bpmnViewer = useRef<BpmnJS | null>(null);

  useEffect(() => {
    if (ref.current) {
      bpmnViewer.current = new BpmnJS({ container: ref.current });
      bpmnViewer.current.importXML(xml).catch(() => {});
    }
    return () => {
      bpmnViewer.current?.destroy();
      bpmnViewer.current = null;
    };
  }, [xml]);

  return <div ref={ref} style={{ height: 500, border: "1px solid #eee" }} />;
};

export default BpmnEditor; 