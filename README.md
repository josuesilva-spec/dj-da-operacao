# DJ da Operação — protótipo funcional

App web local para pedidos de vídeos do YouTube por QR Code, fila compartilhada e player administrativo. Não baixa nem extrai áudio.

## Instalação

1. Instale Python 3.10+ no computador conectado ao som.
2. No terminal, dentro desta pasta, execute `pip install -r requirements.txt`.
3. Defina um PIN próprio: Windows PowerShell: `$env:DJ_ADMIN_PIN="SEU_PIN_FORTE"`; macOS/Linux: `export DJ_ADMIN_PIN="SEU_PIN_FORTE"`.
4. Execute `python server.py`.
5. No computador, abra `http://localhost:8765/admin.html`.
6. Para os celulares, descubra o IP local do computador (Windows: `ipconfig`; Linux/macOS: `ip addr` ou configurações de rede). Abra no computador `http://IP_DO_COMPUTADOR:8765/admin.html` e use o QR Code exibido. Computador e celulares devem ter acesso à mesma rede; o firewall precisa permitir a porta 8765. A rede de visitantes pode bloquear conexões entre aparelhos.
7. Clique em **Ativar player**, informe o PIN e clique em **Próxima música**. Se o navegador exigir, clique em reproduzir no vídeo.

## Pesquisa pelo nome (opcional)

O pedido por link do YouTube funciona sem chave. Para ativar a pesquisa por nome/artista, crie uma chave no Google Cloud com **YouTube Data API v3** habilitada e defina `YOUTUBE_API_KEY` antes de iniciar o servidor. Restrições de chave, cota e faturamento são gerenciadas no Google Cloud. Os resultados de busca são vídeos, não necessariamente faixas musicais oficiais.

## Limitações importantes

- A API oficial do YouTube IFrame pode bloquear autoplay; o usuário pode precisar iniciar a reprodução manualmente. Vídeos podem bloquear incorporação, ser indisponíveis ou conter anúncios. Não há garantia de reprodução contínua.
- YouTube e direitos autorais: valide os Termos do YouTube, autorização para uso empresarial e licenças aplicáveis à execução pública no Brasil (incluindo ECAD quando aplicável). Este protótipo não confere direitos de execução pública.
- A fila fica **na memória** e é perdida ao reiniciar. Este é um protótipo para rede local, sem autenticação individual, moderação de conteúdo, limitação por pessoa ou persistência.
- Não exponha este servidor diretamente à internet. Para implantação real, acrescente HTTPS, autenticação, banco de dados, controles de conteúdo e um serviço de reprodução com licença adequada.
- Se o player chegar ao fim do vídeo, solicita a próxima música. A continuidade depende das políticas do navegador e do YouTube.
