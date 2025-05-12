import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Layout from "../../components/Layout";
import AgentCard from "../../components/AgentCard";
import { Card, Spin, Button, Input, Form, message } from "antd";

const AgentPage: React.FC = () => {
  const router = useRouter();
  const { id } = router.query;
  const [agent, setAgent] = useState<any>(null);
  const [step, setStep] = useState<any>(null);
  const [state, setState] = useState<any>(null);
  const [context, setContext] = useState<any>(null);
  const [inputData, setInputData] = useState<string>("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (id) {
      setLoading(true);
      fetch(`/api/agents/${id}`)
        .then((res) => res.json())
        .then((data) => setAgent(data))
        .catch(() => message.error("Ошибка загрузки агента"));
      fetch(`/api/agents/${id}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: { user_message: "Старт" } }),
      })
        .then((res) => res.json())
        .then((data) => {
          setStep(data.step);
          setState(data.state);
          setContext(data.context || {});
        })
        .catch(() => message.error("Ошибка запуска сценария"))
        .finally(() => setLoading(false));
    }
  }, [id]);

  const handleNextStep = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/agents/${id}/step`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          input_data: inputData ? JSON.parse(inputData) : {},
          state,
          context,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setStep(data.step);
        setState(data.state);
        setContext(data.context);
        message.success("Переход к следующему шагу");
      } else {
        message.error("Ошибка перехода по шагу");
      }
    } catch {
      message.error("Ошибка перехода по шагу");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <h1>Агент</h1>
      {loading || !agent ? (
        <Spin />
      ) : (
        <>
          <AgentCard name={agent.name} config={agent.config} />
          <Card title="Текущий шаг" style={{ marginTop: 24 }}>
            <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(step, null, 2)}</pre>
            <Form layout="vertical" style={{ marginTop: 16 }}>
              <Form.Item label="input_data (JSON)">
                <Input.TextArea
                  rows={2}
                  value={inputData}
                  onChange={e => setInputData(e.target.value)}
                  placeholder="{\"x\": 5}"
                />
              </Form.Item>
              <Button type="primary" onClick={handleNextStep}>
                Следующий шаг
              </Button>
            </Form>
            <div style={{ marginTop: 16 }}>
              <b>state:</b>
              <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(state, null, 2)}</pre>
              <b>context:</b>
              <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(context, null, 2)}</pre>
            </div>
          </Card>
        </>
      )}
    </Layout>
  );
};

export default AgentPage; 