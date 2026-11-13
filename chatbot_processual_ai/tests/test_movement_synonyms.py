import unittest

from agents import agent3_process_analysis as agent3
from services.text_normalization import normalize_text_for_match


class SinonimosDeMovimentacaoTestCase(unittest.TestCase):
    """"Movimentos" e "andamentos" pedem a mesma lista que "movimentações"."""

    def _lista(self, pergunta: str) -> bool:
        normalizada = normalize_text_for_match(pergunta)
        return agent3._mentions_movement(normalizada) and agent3._is_movement_list_question(normalizada)

    def test_movimentos_pede_a_lista(self):
        # pergunta real que caía na resposta genérica
        self.assertTrue(self._lista("Quais são os movimentos dele até hoje?"))

    def test_andamentos_pede_a_lista(self):
        self.assertTrue(self._lista("Quais os andamentos do processo?"))

    def test_movimentacoes_continua_pedindo_a_lista(self):
        self.assertTrue(self._lista("Quais são as movimentações?"))

    def test_ate_hoje_pede_o_historico_inteiro(self):
        normalizada = normalize_text_for_match("Quais são os movimentos dele até hoje?")
        self.assertTrue(agent3._is_all_movements_question(normalizada))

    def test_sem_marcador_de_tudo_nao_e_historico_inteiro(self):
        normalizada = normalize_text_for_match("Quais são os movimentos?")
        self.assertFalse(agent3._is_all_movements_question(normalizada))

    def test_ultimo_movimento_nao_vira_lista(self):
        self.assertFalse(self._lista("Qual foi o último movimento?"))


if __name__ == "__main__":
    unittest.main()
