import logging
logging.level=logging.INFO
from typing import Dict, List
import pandas as pd
from ambima_connect import AmbimaConnect
from sql_connect import send_to_sql
from io import StringIO
import requests
from titulos import LTN, NTNB, NTNF, LFT, Priv
from datetime import date, datetime

def format_date(date_str):
    try: # format /
        return f"\'{datetime.strptime(date_str, '%d/%m/%Y').date()}\'"
    except:
        return f"\'{datetime.strptime(date_str, '%Y-%m-%d').date()}\'"

def format_for_query(raw):
    try:
        try:
            raw_int = int(raw)
            raw = raw_int
        except:
            raw_float = float(str(raw).replace(',','.'))
            raw = raw_float
        if str(raw).lower() == 'nan':
            return 'NULL'
        else:
            return f"'{raw}'"
    except:
        if raw.lower() == 'nan' or raw.lower().replace(' ','') == '-':
            return 'NULL'
        elif raw.lower() == 'n':
            return '0'
        elif raw.lower() == 's':
            return '1'
        try:
            return format_date(raw)
        except:
            return f"'{raw}'"

def list_debentures():
    url_list = 'http://www.debentures.com.br/exploreosnd/consultaadados/emissoesdedebentures/caracteristicas_e.asp?op_exc=False'
    results_list = requests.get(url_list)
    csvString_list=results_list.content.decode('Windows 1254')
    csvStringIO_list = StringIO(csvString_list)
    df_list = pd.read_csv(csvStringIO_list, sep="\t", index_col=False, skiprows=[0,1,2])
    ativos = df_list['Codigo do Ativo'].str.replace(' ', '').tolist()
    return ativos

def public():
    public_list = AmbimaConnect('titulos publicos').content

    for titulo in public_list[:10]:
        if titulo['tipo_titulo'] == 'LTN':
            calc = LTN(
                data_venc=titulo['data_vencimento'],
                taxa=titulo['taxa_indicativa']/100,
                data_ref=titulo['data_referencia'],
                )
        elif titulo['tipo_titulo'] == 'NTN-B':
            calc = NTNB(
                data_venc=titulo['data_vencimento'],
                taxa=titulo['taxa_indicativa']/100,
                data_ref=titulo['data_referencia'],
                )
        elif titulo['tipo_titulo'] == 'NTN-F':
            calc = NTNF(
                data_venc=titulo['data_vencimento'],
                taxa=titulo['taxa_indicativa']/100,
                data_ref=titulo['data_referencia'],
                )
        elif titulo['tipo_titulo'] == 'LFT':
            calc = LFT(
                data_venc=titulo['data_vencimento'],
                taxa=titulo['taxa_indicativa']/100,
                data_ref=titulo['data_referencia'],
                )
        send_to_sql(
            f"""INSERT INTO `develop`.`titulos_publicos`(
                `tipo_titulo`,
                `expressao`,
                `data_vencimento`,
                `data_referencia`,
                `codigo_selic`,
                `data_base`,
                `taxa_compra`,
                `taxa_venda`,
                `taxa_indicativa`,
                `intervalo_min_d0`,
                `intervalo_max_d0`,
                `intervalo_min_d1`,
                `intervalo_max_d1`,
                `pu`,
                `pu_calc`,
                `pm`,
                `duration`
            )
            VALUES (
                {format_for_query(calc.tipo)},
                {format_for_query(titulo['expressao'])},
                {format_for_query(titulo['data_vencimento'])},
                {format_for_query(titulo['data_referencia'])},
                {format_for_query(titulo['codigo_selic'])},
                {format_for_query(titulo['data_base'])},
                {format_for_query(titulo['taxa_compra'])},
                {format_for_query(titulo['taxa_venda'])},
                {format_for_query(titulo['taxa_indicativa'])},
                {format_for_query(titulo['intervalo_min_d0'])},
                {format_for_query(titulo['intervalo_max_d0'])},
                {format_for_query(titulo['intervalo_min_d1'])},
                {format_for_query(titulo['intervalo_max_d1'])},
                {format_for_query(titulo['pu'])},
                {format_for_query(calc.pu)},
                {format_for_query(calc.pm)},
                {format_for_query(calc.duration)});"""
            )

def debenture():
    deb_list = list_debentures()

    for codigo in deb_list[:25]:
        deb = Priv(codigo_ativo=codigo)

        send_to_sql(
            f"""INSERT INTO `develop`.`debentures`(
                `codigo_do_ativo`,
                `empresa`,
                `serie`,
                `emissao`,
                `IPO`,
                `situacao`,
                `isin`,
                `registro_cvm_emissao`,
                `data_registro_cvm_emissao`,
                `registro_cvm_programa`,
                `data_emissao`,
                `data_vencimento`,
                `motivo_saida`,
                `data_saida_novo_venc`,
                `data_inicio_rentabilidade`,
                `data_inicio_distribuicao`,
                `ato_societario_1`,
                `data_ato_1`,
                `forma`,
                `garantia_especie`,
                `classe`,
                `quantidade_emitida`,
                `artigo_14`,
                `artigo_24`,
                `quantidade_em_mercado`,
                `quantidade_em_tesouraria`,
                `quantidade_resgatada`,
                `quantidade_cancelada`,
                `quantidade_convertida_no_snd`,
                `quantidade_convertida_fora_do_snd`,
                `quantidade_permutada_no_snd`,
                `quantidade_permutada_fora_do_snd`,
                `unidade_monetaria_1`,
                `valor_nominal_emissao`,
                `unidade_monetaria_2`,
                `valor_nominal_atual`,
                `data_ult_vna`,
                `indice`,
                `tipo`,
                `criterio_de_calculo`,
                `dia_ref_para_indice_precos`,
                `criterio_indice`,
                `corrige_a_cada`,
                `percentual_multiplicador_rentabilidade`,
                `limite_tjlp`,
                `tipo_de_tratamento_limite_tjlp`,
                `juros_criterio_antigo_snd`,
                `premios_criteiro_antigo_snd`,
                `amortizacao_taxa`,
                `amortizacao_cada`,
                `amortizacao_unidade`,
                `amortizacao_carencia`,
                `amortizacao_criterio`,
                `amortizacao_tipo`,
                `juros_criterio_novo_taxa`,
                `juros_criterio_novo_prazo`,
                `juros_criterio_novo_cada`,
                `juros_criterio_novo_unidade`,
                `juros_criterio_novo_carencia`,
                `juros_criterio_novo_criterio`,
                `juros_criteiro_novo_tipo`,
                `premio_criterio_novo_taxa`,
                `premio_criterio_novo_prazo`,
                `premio_criteiro_novo_cada`,
                `premio_criteiro_novo_unidade`,
                `premio_criterio_novo_carencia`,
                `premio_criterio_novo_criterio`,
                `premio_criterio_novo_tipo`,
                `participacao_taxa`,
                `participacao_cada`,
                `participacao_unidade`,
                `participacao_carencia`,
                `participacao_descricao`,
                `banco_mandatario`,
                `agente_fiduciario`,
                `instituicao_depositaria`,
                `coodenador_lider`,
                `CNPJ`,
                `deb_incent_lei_12431`,
                `escritura_padronizada`,
                `resgate_antecipado`,
                `pm`,
                `duration`
            )
            VALUES (
                {format_for_query(deb.codigo_ativo)},
                {format_for_query(deb.caracteristicas['Empresa        '].values[0])},
                {format_for_query(deb.caracteristicas['Serie'].values[0])},
                {format_for_query(deb.caracteristicas['Emissao'].values[0])},
                {format_for_query(deb.caracteristicas['IPO'].values[0])},
                {format_for_query(deb.caracteristicas['Situacao'].values[0])},
                {format_for_query(deb.caracteristicas['ISIN'].values[0])},
                {format_for_query(deb.caracteristicas['Registro CVM da Emissao'].values[0])},
                {format_for_query(deb.caracteristicas['Data de Registro CVM da Emissao'].values[0])},
                {format_for_query(deb.caracteristicas['Registro CVM do Programa'].values[0])},
                {format_for_query(deb.caracteristicas['Data de Emissao'].values[0])},
                {format_for_query(deb.caracteristicas[' Data de Vencimento'].values[0])},
                {format_for_query(deb.caracteristicas['Motivo de Saida '].values[0])} ,
                {format_for_query(deb.caracteristicas['Data de Saida / Novo Vencimento'].values[0])},
                {format_for_query(deb.caracteristicas[' Data do Inicio da Rentabilidade'].values[0])},
                {format_for_query(deb.caracteristicas['Data do Inicio da Distribuicao'].values[0])},
                {format_for_query(deb.caracteristicas['Ato Societario (1)'].values[0])},
                {format_for_query(deb.caracteristicas['Data do Ato (1)'].values[0])},
                {format_for_query(deb.caracteristicas['Forma'].values[0])},
                {format_for_query(deb.caracteristicas['Garantia/Especie'].values[0])},
                {format_for_query(deb.caracteristicas['Classe'].values[0])},
                {format_for_query(deb.caracteristicas['Quantidade Emitida'].values[0])},
                {format_for_query(deb.caracteristicas['Artigo 14'].values[0])},
                {format_for_query(deb.caracteristicas['Artigo 24'].values[0])},
                {format_for_query(deb.caracteristicas['Quantidade em Mercado'].values[0])},
                {format_for_query(deb.caracteristicas['Quantidade em Tesouraria'].values[0])},
                {format_for_query(deb.caracteristicas['Quantidade Resgatada'].values[0])},
                {format_for_query(deb.caracteristicas['Quantidade  Cancelada'].values[0])},
                {format_for_query(deb.caracteristicas['Quantidade Convertida no SND'].values[0])},
                {format_for_query(deb.caracteristicas['Quantidade Convertida fora do SND'].values[0])},
                {format_for_query(deb.caracteristicas['Quantidade Permutada no SND'].values[0])},
                {format_for_query(deb.caracteristicas['Quantidade Permutada fora do SND'].values[0])},
                {format_for_query(deb.caracteristicas['Unidade Monetaria'].values[0])},
                {format_for_query(deb.caracteristicas['Valor Nominal na Emissao'].values[0])},
                {format_for_query(deb.caracteristicas['Unidade Monetaria'].values[0])},
                {format_for_query(deb.caracteristicas['Valor Nominal Atual'].values[0])},
                {format_for_query(deb.caracteristicas['Data Ult. VNA'].values[0])},
                {format_for_query(deb.caracteristicas['indice'].values[0])},
                {format_for_query(deb.caracteristicas['Tipo'].values[0])},
                {format_for_query(deb.caracteristicas['Criterio de Calculo'].values[0])},
                {format_for_query(deb.caracteristicas['Dia de Referencia para indice de Precos'].values[0])},
                {format_for_query(deb.caracteristicas['Criterio para indice'].values[0])},
                {format_for_query(deb.caracteristicas['Corrige a cada'].values[0])},
                {format_for_query(deb.caracteristicas['Percentual Multiplicador/Rentabilidade'].values[0])},
                {format_for_query(deb.caracteristicas['Limite da TJLP'].values[0])},
                {format_for_query(deb.caracteristicas['Tipo de Tratamento do Limite da TJLP'].values[0])},
                {format_for_query(deb.caracteristicas['Juros Criterio Antigo do SND'].values[0])},
                {format_for_query(deb.caracteristicas['Premios Criterio Antigo do SND'].values[0])},
                {format_for_query(deb.caracteristicas['Amortizacao - Taxa'].values[0])},
                {format_for_query(deb.caracteristicas['Amortizacao - Cada'].values[0])},
                {format_for_query(deb.caracteristicas['Amortizacao - Unidade'].values[0])},
                {format_for_query(deb.caracteristicas['Amortizacao - Carencia'].values[0])},
                {format_for_query(deb.caracteristicas['Amortizacao - Criterio'].values[0])},
                {format_for_query(deb.caracteristicas['Tipo de Amortizacao'].values[0])},
                {format_for_query(deb.caracteristicas['Juros Criterio Novo - Taxa'].values[0])},
                {format_for_query(deb.caracteristicas['Juros Criterio Novo - Prazo'].values[0])},
                {format_for_query(deb.caracteristicas['Juros Criterio Novo - Cada'].values[0])},
                {format_for_query(deb.caracteristicas['Juros Criterio Novo - Unidade'].values[0])},
                {format_for_query(deb.caracteristicas['Juros Criterio Novo - Carencia'].values[0])},
                {format_for_query(deb.caracteristicas['Juros Criterio Novo - Criterio'].values[0])},
                {format_for_query(deb.caracteristicas['Juros Criterio Novo - Tipo'].values[0])},
                {format_for_query(deb.caracteristicas['Premio Criterio Novo - Taxa'].values[0])},
                {format_for_query(deb.caracteristicas['Premio Criterio Novo - Prazo'].values[0])},
                {format_for_query(deb.caracteristicas['Premio Criterio Novo - Cada'].values[0])},
                {format_for_query(deb.caracteristicas['Premio Criterio Novo - Unidade'].values[0])},
                {format_for_query(deb.caracteristicas['Premio Criterio Novo - Carencia'].values[0])},
                {format_for_query(deb.caracteristicas['Premio Criterio Novo - Criterio'].values[0])},
                {format_for_query(deb.caracteristicas['Premio Criterio Novo - Tipo'].values[0])},
                {format_for_query(deb.caracteristicas['Participacao - Taxa'].values[0])},
                {format_for_query(deb.caracteristicas['Participacao - Cada'].values[0])},
                {format_for_query(deb.caracteristicas['Participacao - Unidade'].values[0])},
                {format_for_query(deb.caracteristicas['Participacao - Carencia'].values[0])},
                {format_for_query(deb.caracteristicas['Participacao - Descricao'].values[0])},
                {format_for_query(deb.caracteristicas['Banco Mandatario'].values[0])},
                {format_for_query(deb.caracteristicas['Agente Fiduciario'].values[0])},
                {format_for_query(deb.caracteristicas['Instituicao Depositaria'].values[0])},
                {format_for_query(deb.caracteristicas['Coordenador Lider'].values[0])},
                {format_for_query(deb.caracteristicas['CNPJ'].values[0])},
                {format_for_query(deb.caracteristicas['Deb. Incent. (Lei 12.431)'].values[0])},
                {format_for_query(deb.caracteristicas['Escritura Padronizada'].values[0])},
                {format_for_query(deb.caracteristicas['Resgate Antecipado'].values[0])},
                {format_for_query(deb.pm)},
                {format_for_query(deb.duration)}
            );"""
        )

def handler():
    public()
    # debenture()

if __name__ == "__main__":
    handler()
