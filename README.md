# ✨ Three.js Glass Shader — Refração & Aberração Cromática

> Um experimento visual interativo explorando o poder dos **Custom Shaders (GLSL)** e renderização em tempo real com **Three.js**.

![Demonstração do Projeto](https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPOSITORIO/main/preview.png)
*(Dica: você pode colocar uma screenshot ou gif aqui depois!)*

---

## 🎯 Sobre o Projeto

Este projeto nasceu como parte dos meus estudos em **Computação Gráfica para Web (WebGL)**. O objetivo foi recriar no navegador a física visual de um objeto de **vidro/cristal espesso**, daqueles que distorcem o que está atrás e quebram a luz em pequenos arco-íris nas bordas.

Em vez de usar apenas os materiais prontos do Three.js, foi criado um **Shader customizado do zero** escrito em **GLSL** (uma linguagem focada em conversar diretamente com a placa de vídeo).

---

## 🧪 Como a mágica acontece? (Sem complicar!)

Para criar a ilusão de um vidro realista na tela, foram combinados 4 conceitos principais:

1. **Multi-Pass com FBO (A "Foto" do Fundo):**  
   Antes de desenhar o vidro, o computador esconde o objeto por um milésimo de segundo, tira uma "foto" de tudo o que está atrás dele e salva na memória.
   
2. **Refração Vetorial:**  
   Quando o vidro é desenhado por cima, o Shader consulta essa "foto" do fundo, mas entorta os pixels com base nas curvas do objeto. É o mesmo efeito de olhar através de uma garrafa d'água.

3. **RGB Split (Aberração Cromática):**  
   Na física real, a luz vermelha, verde e azul viajam em velocidades ligeiramente diferentes dentro do vidro. No código, deslocamos essas 3 cores separadamente na hora de buscar a imagem de fundo, criando aquelas bordas coloridas estilo "prisma".

4. **Efeito Fresnel & Especular:**  
   Vidros reais refletem mais a luz quando olhamos para eles de lado (ângulo rasante). O efeito Fresnel calcula esse ângulo para dar aquele contorno brilhoso nas pontas.

---

## 🚀 Funcionalidades

- 💎 **Várias Geometrias:** Alterne entre Torus Knot, Esfera, Icosaedro e mais através do menu.
- 🎨 **Fundo 100% Procedural:** Nenhum arquivo de imagem externo é carregado. O xadrez, linhas neon e formas flutuantes são gerados por código (zero problemas com CORS).
- 🖱️ **Zoom Cinemático Suave:** Interpolação suave ao rolar a rodinha do mouse ou fazer pinça no touch, sem travamentos.
- ⚙️ **Painel de Ajustes ao Vivo:** Controle a intensidade da refração, abertura do RGB split, brilho e rotação com a interface `lil-gui`.

---

## 🛠️ Tecnologias Utilizadas

- **[Three.js](https://threejs.org/):** Framework para estruturação da cena 3D, câmera e luzes.
- **GLSL (OpenGL Shading Language):** Vertex Shader e Fragment Shader customizados.
- **JavaScript (ES Modules):** Arquitetura moderna e modular.
- **HTML5 & CSS3:** Interface com estética *glassmorphism*.

---

## 💻 Como Rodar Localmente

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git

Acesse a pasta:

cd NOME_DO_REPOSITORIO

Inicie um servidor local:

Com Python:
python -m http.server 3000

Ou com a extensão Live Server do VS Code.

Abra no seu navegador:
Acesse http://localhost:3000
