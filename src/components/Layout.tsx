import React, { PropsWithChildren } from "react";
import { Layout as AntLayout, Menu } from "antd";
import Link from "next/link";

const { Header, Content, Footer } = AntLayout;

const items = [
  { key: "agents", label: <Link href="/agents">Агенты</Link> },
  { key: "scenarios", label: <Link href="/scenarios">Сценарии</Link> },
  { key: "logs", label: <Link href="/logs">Логи</Link> },
];

const Layout: React.FC<PropsWithChildren> = ({ children }) => (
  <AntLayout style={{ minHeight: "100vh" }}>
    <Header style={{ display: "flex", alignItems: "center" }}>
      <div style={{ color: "#fff", fontWeight: 700, fontSize: 20, marginRight: 32 }}>
        Universal Agent Platform
      </div>
      <Menu theme="dark" mode="horizontal" items={items} style={{ flex: 1 }} />
    </Header>
    <Content style={{ padding: 24, maxWidth: 1000, margin: "0 auto", width: "100%" }}>
      {children}
    </Content>
    <Footer style={{ textAlign: "center" }}>
      Universal Agent Platform © {new Date().getFullYear()}
    </Footer>
  </AntLayout>
);

export default Layout; 