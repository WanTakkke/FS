import { useEffect } from "react";
import { App as AntdApp } from "antd";
import type { MessageInstance } from "antd/es/message/interface";

let messageApiRef: MessageInstance | null = null;

export function AntdMessageRegistrar() {
  const { message } = AntdApp.useApp();

  useEffect(() => {
    messageApiRef = message;
    return () => {
      if (messageApiRef === message) {
        messageApiRef = null;
      }
    };
  }, [message]);

  return null;
}

export function showErrorMessage(content: string) {
  if (messageApiRef) {
    messageApiRef.error(content);
    return;
  }
  console.error(content);
}
