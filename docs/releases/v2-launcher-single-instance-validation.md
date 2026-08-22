# Hotfix v2 — identidade e instância da GUI

## Alterações

- classe de janela estável `UbuntuAIAssistant`;
- `StartupWMClass` alinhado à janela Tk;
- `StartupNotify` desativado para evitar espera indevida do GNOME;
- arquivo de trava privado por usuário;
- segunda instância impedida;
- ativação interna por `SIGUSR1`;
- encerramento libera a trava automaticamente;
- nenhuma dependência de `wmctrl` ou `xdotool`.

## Validação funcional

- aplicação exibida no `Alt+Tab`;
- processo duplicado deixou de ser criado;
- sinal direto restaurou a janela preservando a conversa;
- launcher e arquivo `.desktop` reinstalados;
- testes automatizados de identidade e instância única adicionados.

## Limitação conhecida

Na sessão GNOME/Wayland testada, clicar no ícone com a janela minimizada ainda
não restaura a janela de forma consistente. O acesso pelo `Alt+Tab` funciona.
Essa limitação não afeta execução, dados ou segurança e permanece registrada
para manutenção futura.
