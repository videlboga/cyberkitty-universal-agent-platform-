import React, { useState, useEffect } from "react";
import Layout from "../../components/Layout";
import BpmnEditor from "../../components/BpmnEditor";
import { Button, message, Spin, Input } from "antd";
import { useRouter } from "next/router";

const defaultXml = `<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" id="Definitions_1" targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="Process_1" isExecutable="false">
    <bpmn:startEvent id="StartEvent_1"/>
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="_BPMNShape_StartEvent_2" bpmnElement="StartEvent_1">
        <dc:Bounds x="173" y="102" width="36" height="36"/>
      </bpmndi:BPMNShape>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>`;

const ScenarioEditorPage: React.FC = () => {
  const router = useRouter();
  const { id } = router.query;
  const [xml, setXml] = useState(defaultXml);
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const editorRef = React.useRef<any>(null);

  useEffect(() => {
    if (id) {
      setLoading(true);
      fetch(`/api/scenarios/${id}`)
        .then((res) => res.json())
        .then((data) => {
          setName(data.name || "");
          setXml(data.bpmn_xml || defaultXml);
          setLoading(false);
        })
        .catch(() => {
          message.error("Ошибка загрузки сценария");
          setLoading(false);
        });
    }
  }, [id]);

  // Получить актуальный xml из редактора (если потребуется)
  const getCurrentXml = async () => {
    if (editorRef.current && editorRef.current.bpmnViewer) {
      try {
        const { xml } = await editorRef.current.bpmnViewer.saveXML({ format: true });
        return xml;
      } catch {
        return xml;
      }
    }
    return xml;
  };

  const handleSave = async () => {
    setLoading(true);
    const method = id ? "PATCH" : "POST";
    const url = id ? `/api/scenarios/${id}` : "/api/scenarios";
    const bpmn_xml = await getCurrentXml();
    const body = { name, bpmn_xml };
    try {
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (res.ok) {
        message.success("Сценарий сохранён");
        if (!id) {
          const data = await res.json();
          router.replace(`/scenarios/editor?id=${data.id}`);
        }
      } else {
        message.error("Ошибка сохранения сценария");
      }
    } catch {
      message.error("Ошибка сохранения сценария");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <h1 style={{ marginBottom: 24 }}>Редактор сценария (BPMN)</h1>
      {loading ? (
        <Spin />
      ) : (
        <>
          <Input
            placeholder="Название сценария"
            value={name}
            onChange={e => setName(e.target.value)}
            style={{ marginBottom: 16, maxWidth: 400 }}
          />
          <BpmnEditor ref={editorRef} xml={xml} />
          <Button type="primary" style={{ marginTop: 16 }} onClick={handleSave}>
            Сохранить
          </Button>
        </>
      )}
    </Layout>
  );
};

export default ScenarioEditorPage; 