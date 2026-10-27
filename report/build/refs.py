"""IEEE-style references. Numbers are assigned in order of first citation; uncited entries are omitted."""

REFS = {
    "ribeiro2016": 'M. T. Ribeiro, S. Singh, and C. Guestrin, "‘Why should I trust you?’: Explaining the predictions of '
                   'any classifier," in *Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining (KDD)*, '
                   'San Francisco, CA, USA, 2016, pp. 1135–1144, doi: 10.1145/2939672.2939778.',
    "lundberg2017": 'S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting model predictions," in *Advances in '
                    'Neural Information Processing Systems 30 (NeurIPS)*, Long Beach, CA, USA, 2017, pp. 4765–4774.',
    "lundberg2020": 'S. M. Lundberg, G. Erion, H. Chen, A. DeGrave, J. M. Prutkin, B. Nair, R. Katz, J. Himmelfarb, N. Bansal, '
                    'and S.-I. Lee, "From local explanations to global understanding with explainable AI for trees," '
                    '*Nature Machine Intelligence*, vol. 2, no. 1, pp. 56–67, 2020, doi: 10.1038/s42256-019-0138-9.',
    "shapley1953": 'L. S. Shapley, "A value for n-person games," in *Contributions to the Theory of Games*, vol. II, '
                   'H. W. Kuhn and A. W. Tucker, Eds. Princeton, NJ, USA: Princeton Univ. Press, 1953, pp. 307–317.',
    "breiman2001": 'L. Breiman, "Random forests," *Machine Learning*, vol. 45, no. 1, pp. 5–32, 2001, '
                   'doi: 10.1023/A:1010933404324.',
    "street1993": 'W. N. Street, W. H. Wolberg, and O. L. Mangasarian, "Nuclear feature extraction for breast tumor diagnosis," '
                  'in *Proc. SPIE 1905, Biomedical Image Processing and Biomedical Visualization*, San Jose, CA, USA, 1993, '
                  'pp. 861–870, doi: 10.1117/12.148698.',
    "uci1995": 'W. Wolberg, O. Mangasarian, N. Street, and W. Street, "Breast Cancer Wisconsin (Diagnostic)," UCI Machine '
               'Learning Repository, 1993, doi: 10.24432/C5DW2B.',
    "pedregosa2011": 'F. Pedregosa *et al.*, "Scikit-learn: Machine learning in Python," *J. Mach. Learn. Res.*, vol. 12, '
                     'pp. 2825–2830, 2011.',
    "rudin2019": 'C. Rudin, "Stop explaining black box machine learning models for high stakes decisions and use interpretable '
                 'models instead," *Nature Machine Intelligence*, vol. 1, no. 5, pp. 206–215, 2019, '
                 'doi: 10.1038/s42256-019-0048-x.',
    "doshivelez2017": 'F. Doshi-Velez and B. Kim, "Towards a rigorous science of interpretable machine learning," 2017, '
                      'arXiv:1702.08608.',
    "lipton2018": 'Z. C. Lipton, "The mythos of model interpretability," *Commun. ACM*, vol. 61, no. 10, pp. 36–43, 2018, '
                  'doi: 10.1145/3233231.',
    "adadi2018": 'A. Adadi and M. Berrada, "Peeking inside the black-box: A survey on explainable artificial intelligence (XAI)," '
                 '*IEEE Access*, vol. 6, pp. 52138–52160, 2018, doi: 10.1109/ACCESS.2018.2870052.',
    "arrieta2020": 'A. Barredo Arrieta *et al.*, "Explainable artificial intelligence (XAI): Concepts, taxonomies, opportunities '
                   'and challenges toward responsible AI," *Information Fusion*, vol. 58, pp. 82–115, 2020, '
                   'doi: 10.1016/j.inffus.2019.12.012.',
    "holzinger2017": 'A. Holzinger, C. Biemann, C. S. Pattichis, and D. B. Kell, "What do we need to build explainable AI systems '
                     'for the medical domain?," 2017, arXiv:1712.09923.',
    "alvarez2018": 'D. Alvarez-Melis and T. S. Jaakkola, "On the robustness of interpretability methods," presented at the ICML '
                   'Workshop on Human Interpretability in Machine Learning, Stockholm, Sweden, 2018, arXiv:1806.08049.',
    "slack2020": 'D. Slack, S. Hilgard, E. Jia, S. Singh, and H. Lakkaraju, "Fooling LIME and SHAP: Adversarial attacks on post '
                 'hoc explanation methods," in *Proc. AAAI/ACM Conf. AI, Ethics, and Society (AIES)*, New York, NY, USA, 2020, '
                 'pp. 180–186, doi: 10.1145/3375627.3375830.',
    "krishna2022": 'S. Krishna, T. Han, A. Gu, J. Pombra, S. Jabbari, S. Wu, and H. Lakkaraju, "The disagreement problem in '
                   'explainable machine learning: A practitioner’s perspective," 2022, arXiv:2202.01602.',
    "ribeiro2018": 'M. T. Ribeiro, S. Singh, and C. Guestrin, "Anchors: High-precision model-agnostic explanations," in '
                   '*Proc. AAAI Conf. Artificial Intelligence*, vol. 32, no. 1, New Orleans, LA, USA, 2018, pp. 1527–1535, '
                   'doi: 10.1609/aaai.v32i1.11491.',
    "molnar2022": 'C. Molnar, *Interpretable Machine Learning: A Guide for Making Black Box Models Explainable*, 2nd ed., 2022. '
                  '[Online]. Available: https://christophm.github.io/interpretable-ml-book/',
    "niculescu2005": 'A. Niculescu-Mizil and R. Caruana, "Predicting good probabilities with supervised learning," in *Proc. 22nd '
                     'Int. Conf. Machine Learning (ICML)*, Bonn, Germany, 2005, pp. 625–632, doi: 10.1145/1102351.1102430.',
    "who2024bc": 'World Health Organization, "Breast cancer," WHO fact sheet. [Online]. Available: '
                 'https://www.who.int/news-room/fact-sheets/detail/breast-cancer',
    "who2021": 'World Health Organization, *Ethics and Governance of Artificial Intelligence for Health: WHO Guidance*. Geneva, '
               'Switzerland: WHO, 2021, ISBN: 978-92-4-002920-0.',
    "euaiact2024": 'European Parliament and Council of the European Union, "Regulation (EU) 2024/1689 laying down harmonised '
                   'rules on artificial intelligence (Artificial Intelligence Act)," *Official Journal of the European Union*, '
                   'L series, 12 Jul. 2024.',
    "dpdp2023": 'Government of India, "The Digital Personal Data Protection Act, 2023," Act No. 22 of 2023, Ministry of Law and '
                'Justice, New Delhi, India, Aug. 2023.',
    "icmr2023": 'Indian Council of Medical Research, *Ethical Guidelines for Application of Artificial Intelligence in Biomedical '
                'Research and Healthcare*. New Delhi, India: ICMR, 2023.',
    "iso23894": 'ISO/IEC 23894:2023, *Information technology — Artificial intelligence — Guidance on risk management*, '
                'International Organization for Standardization, Geneva, Switzerland, 2023.',
    "ieee2019ead": 'The IEEE Global Initiative on Ethics of Autonomous and Intelligent Systems, *Ethically Aligned Design: A Vision '
                   'for Prioritizing Human Well-being with Autonomous and Intelligent Systems*, 1st ed. IEEE, 2019.',
    "un2015": 'United Nations General Assembly, "Transforming our world: The 2030 Agenda for Sustainable Development," '
              'Resolution A/RES/70/1, Oct. 2015.',
    "shapdocs": 'S. M. Lundberg *et al.*, "SHAP (SHapley Additive exPlanations) documentation." [Online]. Available: '
                'https://shap.readthedocs.io',
    "limerepo": 'M. T. Ribeiro, "LIME: Explaining the predictions of any machine learning classifier," GitHub repository. '
                '[Online]. Available: https://github.com/marcotcr/lime',
    "streamlitdocs": 'Snowflake Inc., "Streamlit documentation." [Online]. Available: https://docs.streamlit.io',
}


class Citations:
    def __init__(self):
        self.order: list[str] = []

    def __call__(self, *keys: str) -> str:
        nums = []
        for k in keys:
            if k not in REFS:
                raise KeyError(k)
            if k not in self.order:
                self.order.append(k)
            nums.append(self.order.index(k) + 1)
        return "[" + "], [".join(str(n) for n in nums) + "]"
