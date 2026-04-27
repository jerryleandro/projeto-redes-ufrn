# Projeto Redes 2

Projeto academico da disciplina Redes 2 demonstrando uma arquitetura local com Docker Compose, Nginx, reverse proxy, dois tenants e DNS em container.

## Estrutura

```text
.
├── dns/
│   └── Corefile
├── gateway/
│   └── nginx.conf
├── tenants/
│   ├── Dockerfile
│   ├── nginx/
│   │   └── default.conf
│   ├── tenant1/
│   │   └── index.html
│   └── tenant2/
│       └── index.html
└── docker-compose.yml
```

## Servicos

| Servico | Container | Funcao |
| --- | --- | --- |
| `dns` | `dns` | Resolve os subdominios locais para o host local |
| `gateway` | `projeto-redes2-gateway` | Recebe HTTP e encaminha pelo host/subdominio |
| `tenant1` | `projeto-redes2-tenant1` | Aplicacao do tenant 1 |
| `tenant2` | `projeto-redes2-tenant2` | Aplicacao do tenant 2 |

## Fluxo

1. O navegador solicita `tenant1.redes2.local` ou `tenant2.redes2.local`.
2. O DNS em container, usando CoreDNS, resolve o subdominio para `127.0.0.1`.
3. A requisicao HTTP chega ao gateway Nginx publicado na porta `80` da maquina local.
4. O gateway le o cabecalho `Host` e encaminha para `tenant1` ou `tenant2` dentro da rede Docker.

O DNS nao faz roteamento por porta. Ele apenas resolve nomes. O roteamento HTTP entre tenants e responsabilidade do gateway.

## Como subir

```bash
docker compose up -d --build
```

Verifique os containers:

```bash
docker compose ps
```

## Como configurar o DNS local

Configure a maquina para usar `127.0.0.1` como servidor DNS local enquanto estiver testando o projeto.

Em Linux com NetworkManager, uma forma comum e ajustar o DNS da conexao ativa para `127.0.0.1`. Tambem e possivel testar diretamente com `dig`:

```bash
dig @127.0.0.1 tenant1.redes2.local
dig @127.0.0.1 tenant2.redes2.local
```

## Como testar

Com o DNS local apontando para `127.0.0.1`, acesse:

```text
http://tenant1.redes2.local
http://tenant2.redes2.local
```

Tambem e possivel testar o gateway sem alterar o DNS do sistema:

```bash
curl -H "Host: tenant1.redes2.local" http://127.0.0.1
curl -H "Host: tenant2.redes2.local" http://127.0.0.1
```

## Encerrar ambiente

```bash
docker compose down
```
