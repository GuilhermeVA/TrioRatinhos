# Projeto de Detecção e Estimação de Velocidade de Veículos

## Hardware
- **Notebook**

## Softwares Utilizados
- **Visual Studio Code (VSCode):** Utilizado para o desenvolvimento do projeto na linguagem Python.  
- **YOLOv8:** Responsável pela detecção de veículos nos frames.  
- **SORT:** Utilizado para o rastreamento contínuo dos veículos em movimento.  

## Descrição do Projeto
Nosso projeto utiliza técnicas de visão computacional e inteligência artificial para realizar a detecção e a estimação da velocidade de veículos em vídeos. Após uma pesquisa aprofundada, utilizamos modelos preexistentes para o reconhecimento inicial dos veículos e, posteriormente, adaptamos o algoritmo para calcular e exibir a velocidade com base no deslocamento dos veículos ao longo dos frames.

### Principais Melhorias no Algoritmo
Para melhorar a precisão das estimativas de velocidade, implementamos diversas otimizações, incluindo:  
1. **Uso da Média Móvel:** Para suavizar os valores e reduzir flutuações.  
2. **Aprimoramento na Conversão de Pixels para Metros:** Ajustamos os cálculos para maior correspondência com medidas reais.  
3. **Utilização de Linhas de Profundidade:** Incorporadas para considerar a perspectiva e aprimorar a exatidão dos cálculos.

### Principais Desafios e Soluções
A maior dificuldade enfrentada foi lidar com a alta flutuação nos valores de velocidade estimados. As melhorias implementadas, especialmente a média móvel e a calibração da conversão de pixels para o mundo real, mostraram-se eficazes para reduzir essas variações, permitindo obter resultados aceitáveis e mais precisos.

## Conclusão
Com as adaptações realizadas, o projeto atingiu resultados satisfatórios no monitoramento e na estimação de velocidades. 

