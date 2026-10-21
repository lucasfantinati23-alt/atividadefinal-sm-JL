# Importa o framework streamlit para a construção da interface do aplicativo web
import streamlit as st
# Importa a biblioteca pandas para a leitura e manipulação das planilhas de dados
import pandas as pd
# Importa o utilitário de divisão de dados entre grupos de treino e de teste
from sklearn.model_selection import train_test_split
# Importa o algoritmo de regressão logística para ajuste e cálculo probabilístico
from sklearn.linear_model import LogisticRegression
# Importa a biblioteca plotly graph objects para gerar os gráficos personalizados e indicadores
import plotly.graph_objects as go

# Define as configurações iniciais de layout da página do app para o formato expandido (wide)
st.set_page_config(layout='wide')

# Adiciona o título visual destacado no topo da página do aplicativo de crédito
st.title('Previsão de Inadimplência de Clientes em Tempo Real')

# Realiza o carregamento da base de dados de inadimplência a partir da planilha copiada
dados = pd.read_excel('inadimplencia-clientes.xlsx')
# Executa a limpeza básica excluindo linhas duplicadas remanescentes da planilha
dados = dados.drop_duplicates()
# Executa a limpeza excluindo todas as ocorrências de registros com valores faltantes
dados = dados.dropna()

# Cria uma cópia limpa dos dados para preservar os textos originais nos filtros e gráficos históricos
dados_historico = dados.copy()

# Define o mapeamento categórico de escolaridade para converter textos em escalas ordinais
mapeamento_escolaridade = {'Fundamental': 0, 'Médio': 1, 'Superior': 2, 'Pós-graduação': 3}
# Cria uma coluna com os códigos numéricos correspondentes de vínculo empregatício para uso interno
dados['Vínculo_Cod'] = dados['Vínculo Empregatício'].astype('category').cat.codes
# Guarda um dicionário que mapeia o texto do vínculo empregatício de volta ao código correspondente
dic_vinculo = dict(zip(dados['Vínculo Empregatício'], dados['Vínculo_Cod']))

# Realiza a transformação definitiva dos dados categóricos textuais para inteiros preditivos
dados['Escolaridade_Num'] = dados['Escolaridade'].map(mapeamento_escolaridade)
# Converte a coluna original do vínculo para o código numérico gerado na preparação
dados['Vínculo Empregatício_Num'] = dados['Vínculo_Cod']
# Mapeia a coluna textual de imóvel próprio para valores lógicos inteiros (1 e 0)
dados['Imóvel Próprio_Num'] = dados['Imóvel Próprio'].map({'Sim': 1, 'Não': 0})
# Converte a coluna resposta Situação para 1 quando inadimplente e 0 para adimplente
dados['Situação_Num'] = dados['Situação'].map({'Inadimplente': 1, 'Adimplente': 0})

# Isola o conjunto final de dados preditivos excluindo as colunas identificadoras e originais
X = dados[['Idade', 'Escolaridade_Num', 'Vínculo Empregatício_Num', 'Renda Mensal (R$)', 'Valor do Empréstimo (R$)', 'Prazo (meses)', 'Valor da Parcela (R$)', 'Atrasos Anteriores', 'Tempo de Relacionamento (anos)', 'Imóvel Próprio_Num']]
# Isola a coluna resposta codificada para a calibração final do algoritmo
y = dados['Situação_Num']

# Executa a quebra de dados no padrão clássico de 70% de modelagem e 30% de teste
X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, test_size=0.30, random_state=42)

# Instancia o classificador de Regressão Logística com alto limite de refinamento
modelo = LogisticRegression(max_iter=1000)
# Ajusta os coeficientes e treina o algoritmo de regressão para gerar previsões
modelo.fit(X_treino, y_treino)

# Instancia o sistema de duas colunas paralelas no layout principal do Streamlit
coluna_esquerda, coluna_direita = st.columns(2)

# Inicia o bloco de construção dos seletores de entrada de dados na coluna esquerda
with coluna_esquerda:
    # Escreve um título para orientar o preenchimento dos dados do perfil
    st.header('Dados do Cliente')
    # Cria o controle deslizante de idade respeitando os limites originais da base
    idade = st.slider('Idade', int(dados_historico['Idade'].min()), int(dados_historico['Idade'].max()), int(dados_historico['Idade'].mean()))
    # Cria a caixa de seleção com as categorias textuais explícitas de escolaridade
    escolaridade_txt = st.selectbox('Escolaridade', list(mapeamento_escolaridade.keys()))
    # Recupera o valor numérico correspondente baseado na escolha de escolaridade feita pelo usuário
    escolaridade_num = mapeamento_escolaridade[escolaridade_txt]
    # Cria a caixa de seleção com as categorias textuais explícitas de vínculo empregatício
    vinculo_txt = st.selectbox('Vínculo Empregatício', list(dic_vinculo.keys()))
    # Recupera o número inteiro mapeado para a categoria de vínculo selecionada
    vinculo_num = dic_vinculo[vinculo_txt]
    # Cria o controle numérico para renda mensal limitando pelos valores da planilha
    renda = st.number_input('Renda Mensal (R$)', float(dados_historico['Renda Mensal (R$)'].min()), float(dados_historico['Renda Mensal (R$)'].max()), float(dados_historico['Renda Mensal (R$)'].median()))
    # Cria o controle numérico para valor total emprestado segundo limites do histórico
    valor_emp = st.number_input('Valor do Empréstimo (R$)', float(dados_historico['Valor do Empréstimo (R$)'].min()), float(dados_historico['Valor do Empréstimo (R$)'].max()), float(dados_historico['Valor do Empréstimo (R$)'].median()))
    # Cria a entrada para o prazo total de parcelamento do empréstimo em meses
    prazo = st.slider('Prazo (meses)', int(dados_historico['Prazo (meses)'].min()), int(dados_historico['Prazo (meses)'].max()), int(dados_historico['Prazo (meses)'].median()))
    # Cria a entrada numérica para o valor correspondente a cada parcela mensal
    parcela = st.number_input('Valor da Parcela (R$)', float(dados_historico['Valor da Parcela (R$)'].min()), float(dados_historico['Valor da Parcela (R$)'].max()), float(dados_historico['Valor da Parcela (R$)'].median()))
    # Cria o controle de seleção para quantidade histórica de atrasos do cliente
    atrasos = st.slider('Atrasos Anteriores', int(dados_historico['Atrasos Anteriores'].min()), int(dados_historico['Atrasos Anteriores'].max()), int(dados_historico['Atrasos Anteriores'].min()))
    # Cria a entrada numérica para o tempo de conta ativo em anos com a instituição
    tempo_rel = st.slider('Tempo de Relacionamento (anos)', int(dados_historico['Tempo de Relacionamento (anos)'].min()), int(dados_historico['Tempo de Relacionamento (anos)'].max()), int(dados_historico['Tempo de Relacionamento (anos)'].median()))
    # Cria a caixa de seleção de imóvel próprio em texto direto para o usuário escolher
    imovel_txt = st.selectbox('Imóvel Próprio', ['Sim', 'Não'])
    # Mapeia dinamicamente Sim para 1 e Não para 0 conforme as entradas do modelo
    imovel_num = 1 if imovel_txt == 'Sim' else 0

    # Adiciona divisória visual para destacar a nova seção de filtros adicionais de histórico
    st.markdown('---')
    # Cabeçalho identificando que as opções abaixo controlam apenas a visualização de gráficos históricos
    st.subheader('Filtros do Histórico de Clientes')
    # Cria um multiselect para filtrar os vínculos profissionais com todos pré-marcados no início
    opcoes_vinculo = st.multiselect('Filtrar por Vínculo Empregatício', options=list(dic_vinculo.keys()), default=list(dic_vinculo.keys()))
    # Cria um multiselect para filtrar as qualificações de escolaridade com todos pré-marcados no início
    opcoes_escolaridade = st.multiselect('Filtrar por Escolaridade', options=list(mapeamento_escolaridade.keys()), default=list(mapeamento_escolaridade.keys()))

# Inicia o bloco de exibição dos resultados reativos na coluna direita
with coluna_direita:
    # Escreve um título informativo sobre o resultado prognóstico gerado
    st.header('Resultado da Análise')
    # Organiza os dados informados em um DataFrame estruturado no mesmo formato de treino
    novo_cliente = pd.DataFrame([[idade, escolaridade_num, vinculo_num, renda, valor_emp, prazo, parcela, atrasos, tempo_rel, imovel_num]], columns=X.columns)
    # Realiza a previsão binária final a partir do modelo reativo ajustado
    previsao = modelo.predict(novo_cliente)[0]
    # Calcula as probabilidades de classificação para cada classe possível
    probabilidades = modelo.predict_proba(novo_cliente)[0]
    # Extrai especificamente a probabilidade correspondente à classe inadimplente (classe 1)
    probabilidade_inadimplencia = probabilidades[1] * 100
    
    # Estrutura a verificação do resultado previsto para definir o diagnóstico impresso
    if previsao == 1:
        # Exibe um alerta visual avermelhado em caso de previsão de risco de inadimplência
        st.error('Previsão: INADIMPLENTE')
    else:
        # Exibe uma mensagem verde caso a previsão seja de crédito saudável (adimplente)
        st.success('Previsão: ADIMPLENTE')

    # Cria o Gráfico 1 - Indicador de Gauge para ilustrar de 0% a 100% a probabilidade de inadimplência
    fig_gauge = go.Figure(go.Indicator(
        mode='gauge+number',
        value=probabilidade_inadimplencia,
        title={'text': 'Probabilidade de Inadimplência (%)'},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': 'red' if previsao == 1 else 'green'},
            'steps': [
                {'range': [0, 30], 'color': 'lightgreen'},
                {'range': [30, 70], 'color': 'yellow'},
                {'range': [70, 100], 'color': 'salmon'}
            ]
        }
    ))
    # Remove margens desnecessárias do gráfico para otimizar espaço de tela
    fig_gauge.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=220)
    # Renderiza o indicador visual de Gauge na página do aplicativo
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Aplica o filtro de seleção de histórico de clientes com base nas escolhas interativas
    historico_filtrado = dados_historico[
        (dados_historico['Vínculo Empregatício'].isin(opcoes_vinculo)) &
        (dados_historico['Escolaridade'].isin(opcoes_escolaridade))
    ]

    # Verifica se os seletores de filtros deixaram a base filtrada vazia para mostrar um aviso
    if len(opcoes_vinculo) == 0 or len(opcoes_escolaridade) == 0 or historico_filtrado.empty:
        # Mostra um alerta informativo amarelo solicitando que se selecione ao menos uma opção
        st.warning('Selecione pelo menos uma opção nos filtros de Vínculo Empregatício e Escolaridade para visualizar os gráficos.')
    else:
        # Cria o Gráfico 2 - Dispersão de Renda por Parcela
        fig_scatter = go.Figure()

        # Divide os registros históricos filtrados entre adimplentes reais
        adimplentes_hist = historico_filtrado[historico_filtrado['Situação'] == 'Adimplente']
        # Divide os registros históricos filtrados entre inadimplentes reais
        inadimplentes_hist = historico_filtrado[historico_filtrado['Situação'] == 'Inadimplente']

        # Adiciona a série de clientes adimplentes marcados com pontos em azul escuro
        fig_scatter.add_trace(go.Scatter(
            x=adimplentes_hist['Valor da Parcela (R$)'],
            y=adimplentes_hist['Renda Mensal (R$)'],
            mode='markers',
            name='Histórico: Adimplente',
            marker=dict(color='blue', opacity=0.6, size=8)
        ))

        # Adiciona a série de clientes inadimplentes marcados com pontos em vermelho vivo
        fig_scatter.add_trace(go.Scatter(
            x=inadimplentes_hist['Valor da Parcela (R$)'],
            y=inadimplentes_hist['Renda Mensal (R$)'],
            mode='markers',
            name='Histórico: Inadimplente',
            marker=dict(color='red', opacity=0.6, size=8)
        ))

        # Adiciona o marcador em destaque (estrela amarela) para o cliente simulado atualmente
        fig_scatter.add_trace(go.Scatter(
            x=[parcela],
            y=[renda],
            mode='markers',
            name='Cliente Simulado',
            marker=dict(color='yellow', size=18, symbol='star', line=dict(color='black', width=1.5))
        ))

        # Atualiza os rótulos dos eixos e título do gráfico de dispersão com design limpo
        fig_scatter.update_layout(
            title='Dispersão de Clientes: Renda Mensal vs Valor da Parcela',
            xaxis_title='Valor da Parcela (R$)',
            yaxis_title='Renda Mensal (R$)',
            legend=dict(yanchor='top', y=0.99, xanchor='left', x=0.01),
            margin=dict(l=20, r=20, t=40, b=20),
            height=320
        )

        # Renderiza o gráfico de dispersão Plotly construído na página
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Criação do Gráfico 3 - Taxa de Inadimplência por Faixa de Atrasos Anteriores
        # Agrupa os dados filtrados por Atrasos Anteriores e calcula a taxa real de inadimplência de cada quantidade de atrasos
        taxas_atraso = historico_filtrado.groupby('Atrasos Anteriores')['Situação'].apply(lambda s: (s == 'Inadimplente').sum() / len(s) * 100).reset_index()
        taxas_atraso.columns = ['Atrasos Anteriores', 'Taxa de Inadimplência (%)']
        # Garante a ordenação correta das barras no eixo X pelo número de atrasos anteriores
        taxas_atraso = taxas_atraso.sort_values('Atrasos Anteriores')

        # Define uma cor especial para cada barra do gráfico: laranja para a quantidade em que o cliente simulado está, azul para as outras
        cores_barras = []
        for valor_atraso in taxas_atraso['Atrasos Anteriores']:
            if valor_atraso == atrasos:
                # Caso a barra represente o número exato de atrasos selecionado para o cliente, pinta de laranja de destaque
                cores_barras.append('orange')
            else:
                # Caso contrário, aplica a cor azul padrão
                cores_barras.append('royalblue')

        # Cria a figura de barras do Plotly
        fig_bar = go.Figure(data=[go.Bar(
            x=taxas_atraso['Atrasos Anteriores'],
            y=taxas_atraso['Taxa de Inadimplência (%)'],
            marker_color=cores_barras,
            text=[f'{val:.1f}%' for valor_idx, val in enumerate(taxas_atraso['Taxa de Inadimplência (%)'])],
            textposition='auto'
        )])

        # Atualiza o layout e títulos dos eixos para o terceiro gráfico
        fig_bar.update_layout(
            title='Taxa Real de Inadimplência por Quantidade de Atrasos',
            xaxis_title='Atrasos Anteriores (Histórico)',
            yaxis_title='Taxa de Inadimplência (%)',
            xaxis=dict(tickmode='linear', dtick=1),
            margin=dict(l=20, r=20, t=40, b=20),
            height=320
        )

        # Renderiza o novo gráfico de barras interativo no painel do Streamlit
        st.plotly_chart(fig_bar, use_container_width=True)
