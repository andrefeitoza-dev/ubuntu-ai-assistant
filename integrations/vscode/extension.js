"use strict";

const path = require("path");
const { spawn } = require("child_process");
const vscode = require("vscode");

const output = vscode.window.createOutputChannel("Ubuntu AI Assistant");

function configuredExecutable(key, expected) {
  const value = vscode.workspace
    .getConfiguration("ubuntuAI")
    .get(key, expected)
    .trim();
  if (value === expected) {
    return value;
  }
  if (!path.isAbsolute(value) || path.basename(value) !== expected) {
    throw new Error(
      `${key} deve ser '${expected}' ou um caminho absoluto terminado em '${expected}'.`
    );
  }
  return value;
}

function runProcess(executable, args, title, detached = false) {
  output.show(true);
  output.appendLine(`\n> ${executable} ${args.join(" ")}`);
  const child = spawn(executable, args, {
    shell: false,
    windowsHide: true,
    detached,
    stdio: detached ? "ignore" : ["ignore", "pipe", "pipe"],
  });
  if (detached) {
    child.unref();
    return Promise.resolve();
  }
  child.stdout.on("data", (data) => output.append(data.toString()));
  child.stderr.on("data", (data) => output.append(data.toString()));
  return vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title,
      cancellable: true,
    },
    (_progress, token) =>
      new Promise((resolve, reject) => {
        token.onCancellationRequested(() => child.kill("SIGTERM"));
        child.on("error", reject);
        child.on("close", (code) => {
          if (code === 0) {
            resolve();
          } else {
            reject(new Error(`ubuntu-ai terminou com código ${code}.`));
          }
        });
      })
  );
}

async function requestText(prompt) {
  return vscode.window.showInputBox({
    prompt,
    ignoreFocusOut: true,
    validateInput: (value) =>
      value.trim().length === 0 ? "Informe uma solicitação." : undefined,
  });
}

async function safeCommand(args, title) {
  try {
    const executable = configuredExecutable("executable", "ubuntu-ai");
    await runProcess(executable, args, title);
  } catch (error) {
    vscode.window.showErrorMessage(`Ubuntu AI: ${error.message}`);
  }
}

function activate(context) {
  context.subscriptions.push(
    output,
    vscode.commands.registerCommand("ubuntuAI.openGui", async () => {
      try {
        const executable = configuredExecutable("guiExecutable", "ubuntu-ai-gui");
        await runProcess(executable, [], "Abrindo Ubuntu AI", true);
      } catch (error) {
        vscode.window.showErrorMessage(`Ubuntu AI: ${error.message}`);
      }
    }),
    vscode.commands.registerCommand("ubuntuAI.doctor", () =>
      safeCommand(["doctor"], "Verificando ambiente")
    ),
    vscode.commands.registerCommand("ubuntuAI.health", () =>
      safeCommand(["health"], "Consultando saúde")
    ),
    vscode.commands.registerCommand("ubuntuAI.profiles", () =>
      safeCommand(["ecosystem", "profiles"], "Consultando perfis")
    ),
    vscode.commands.registerCommand("ubuntuAI.plan", async () => {
      const request = await requestText("O que deseja planejar?");
      if (request !== undefined) {
        await safeCommand(["plan", request], "Gerando plano seguro");
      }
    }),
    vscode.commands.registerCommand("ubuntuAI.preview", async () => {
      const request = await requestText("Qual ação deseja visualizar sem executar?");
      if (request !== undefined) {
        await safeCommand(["run", "--dry-run", request], "Gerando prévia");
      }
    })
  );
}

function deactivate() {}

module.exports = { activate, deactivate };
