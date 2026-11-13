import unittest
from types import SimpleNamespace

from services.meta_diagnosis_service import _consistent_with


def _diagnostico(*status):
    metas = [SimpleNamespace(meta=f"Meta {i} (x)", status=s) for i, s in enumerate(status, start=1)]
    return SimpleNamespace(metas=metas)


class GuardaDaOrientacaoTestCase(unittest.TestCase):
    def test_aceita_redacao_coerente_com_o_calculo(self):
        texto = ("O processo pesa contra a Meta 1 e não entra na Meta 2. O movimento determinante é "
                 "a distribuição. Para deixar de constar, é preciso a sentença ou a baixa definitiva.")
        self.assertTrue(_consistent_with(texto, _diagnostico("PENDENTE", "FORA")))

    def test_descarta_ato_que_o_calculo_nao_modela(self):
        # caso real: o modelo copiou do glossário hipóteses de julgamento fora da lista calculada
        texto = ("Para deixar de constar, você precisa registrar primeira sentença, procedimento "
                 "resolvido ou decisão em medidas protetivas de urgência.")
        self.assertFalse(_consistent_with(texto, _diagnostico("PENDENTE", "FORA")))

    def test_descarta_peso_nas_duas_metas_quando_so_uma_pesa(self):
        texto = "O processo pesa nas Metas 1 e 2."
        self.assertFalse(_consistent_with(texto, _diagnostico("PENDENTE", "FORA")))


if __name__ == "__main__":
    unittest.main()
