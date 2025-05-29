import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class MedicalEntity:
    text: str
    entity_type: str  # 'disease', 'test', 'value', 'symptom'
    value: Optional[float] = None
    unit: Optional[str] = None
    normal_range: Optional[str] = None

class MedicalAnalyzer:
    def __init__(self):
        # 주요 검사 항목과 정상 범위
        self.lab_values = {
            'crp': {'name': 'C-reactive protein', 'normal': '<3.0 mg/L', 'keywords': ['inflammation', 'acute phase']},
            'hba1c': {'name': 'Hemoglobin A1c', 'normal': '<5.7%', 'keywords': ['diabetes', 'glucose control']},
            'glucose': {'name': 'Blood glucose', 'normal': '70-100 mg/dL', 'keywords': ['diabetes', 'hypoglycemia']},
            'cholesterol': {'name': 'Total cholesterol', 'normal': '<200 mg/dL', 'keywords': ['cardiovascular', 'lipid']},
            'hdl': {'name': 'HDL cholesterol', 'normal': '>40 mg/dL (M), >50 mg/dL (F)', 'keywords': ['cardiovascular']},
            'ldl': {'name': 'LDL cholesterol', 'normal': '<100 mg/dL', 'keywords': ['cardiovascular']},
            'triglyceride': {'name': 'Triglycerides', 'normal': '<150 mg/dL', 'keywords': ['cardiovascular', 'lipid']},
            'bun': {'name': 'Blood urea nitrogen', 'normal': '7-20 mg/dL', 'keywords': ['kidney', 'renal']},
            'creatinine': {'name': 'Creatinine', 'normal': '0.6-1.2 mg/dL', 'keywords': ['kidney', 'renal']},
            'alt': {'name': 'ALT', 'normal': '7-56 U/L', 'keywords': ['liver', 'hepatic']},
            'ast': {'name': 'AST', 'normal': '10-40 U/L', 'keywords': ['liver', 'hepatic']},
            'bp': {'name': 'Blood pressure', 'normal': '<120/80 mmHg', 'keywords': ['hypertension', 'cardiovascular']},
            'wbc': {'name': 'White blood cell count', 'normal': '4,500-11,000/μL', 'keywords': ['infection', 'immune']},
            'rbc': {'name': 'Red blood cell count', 'normal': '4.7-6.1M/μL (M), 4.2-5.4M/μL (F)', 'keywords': ['anemia']},
            'hemoglobin': {'name': 'Hemoglobin', 'normal': '14-18 g/dL (M), 12-16 g/dL (F)', 'keywords': ['anemia']},
            'hematocrit': {'name': 'Hematocrit', 'normal': '42-52% (M), 37-47% (F)', 'keywords': ['anemia']},
            'platelet': {'name': 'Platelet count', 'normal': '150,000-450,000/μL', 'keywords': ['bleeding', 'coagulation']},
            
            # 종양 표지자 추가
            'ca125': {'name': 'CA-125', 'normal': '<35 U/mL', 'keywords': ['ovarian cancer', 'tumor marker', 'gynecologic cancer']},
            'ca-125': {'name': 'CA-125', 'normal': '<35 U/mL', 'keywords': ['ovarian cancer', 'tumor marker', 'gynecologic cancer']},
            'ca 125': {'name': 'CA-125', 'normal': '<35 U/mL', 'keywords': ['ovarian cancer', 'tumor marker', 'gynecologic cancer']},
            'cea': {'name': 'CEA', 'normal': '<3.0 ng/mL', 'keywords': ['colorectal cancer', 'tumor marker']},
            'afp': {'name': 'AFP', 'normal': '<10 ng/mL', 'keywords': ['liver cancer', 'hepatocellular carcinoma', 'tumor marker']},
            'psa': {'name': 'PSA', 'normal': '<4.0 ng/mL', 'keywords': ['prostate cancer', 'tumor marker']},
            'ca19-9': {'name': 'CA 19-9', 'normal': '<37 U/mL', 'keywords': ['pancreatic cancer', 'tumor marker']},
            'ca15-3': {'name': 'CA 15-3', 'normal': '<30 U/mL', 'keywords': ['breast cancer', 'tumor marker']},
            'beta-hcg': {'name': 'Beta-hCG', 'normal': '<5 mIU/mL', 'keywords': ['testicular cancer', 'tumor marker', 'pregnancy']},
            'ldh': {'name': 'LDH', 'normal': '140-280 U/L', 'keywords': ['tissue damage', 'tumor marker']},
        }
        
        # 일반적인 질병명
        self.diseases = {
            '당뇨병': 'diabetes mellitus',
            '고혈압': 'hypertension',
            '파킨슨병': 'parkinson disease',
            '알츠하이머': 'alzheimer disease',
            '심근경색': 'myocardial infarction',
            '뇌졸중': 'stroke',
            '암': 'cancer',
            '관절염': 'arthritis',
            '천식': 'asthma',
            '우울증': 'depression',
            '불안장애': 'anxiety disorder',
            '간염': 'hepatitis',
            '신부전': 'renal failure',
            '심부전': 'heart failure',
            '골다공증': 'osteoporosis',
            # 고지혈증 관련 용어 추가
            '고지혈': 'hyperlipidemia',
            '고지혈증': 'hyperlipidemia',
            '이상지질혈증': 'dyslipidemia',
            '고콜레스테롤혈증': 'hypercholesterolemia',
            '고중성지방혈증': 'hypertriglyceridemia',
            # 기타 심혈관 질환
            '동맥경화': 'atherosclerosis',
            '협심증': 'angina pectoris',
            '부정맥': 'arrhythmia',
            '심방세동': 'atrial fibrillation',
            # 내분비 질환
            '갑상선기능항진증': 'hyperthyroidism',
            '갑상선기능저하증': 'hypothyroidism',
            '비만': 'obesity',
            '대사증후군': 'metabolic syndrome',
            # 소화기 질환
            '위염': 'gastritis',
            '위궤양': 'gastric ulcer',
            '십이지장궤양': 'duodenal ulcer',
            '역류성식도염': 'gastroesophageal reflux disease',
            # 호흡기 질환
            '폐렴': 'pneumonia',
            '기관지염': 'bronchitis',
            '만성폐쇄성폐질환': 'chronic obstructive pulmonary disease',
            # 신경계 질환
            '뇌전증': 'epilepsy',
            '편두통': 'migraine',
            '치매': 'dementia',
            
            # 파킨슨병 관련 용어 추가
            '파킨슨': 'parkinson',
            '파킨슨병': 'parkinson disease',
            '파킨슨증': 'parkinsonism',
            '도파민': 'dopamine',
            '레보도파': 'levodopa',
            'l-dopa': 'levodopa',
            '카비도파': 'carbidopa',
            '도파민작용제': 'dopamine agonist',
            '프라미펙솔': 'pramipexole',
            '로피니롤': 'ropinirole',
            '떨림': 'tremor',
            '진전': 'tremor',
            '경직': 'rigidity',
            '서동증': 'bradykinesia',
            '자세불안정': 'postural instability',
            '보행장애': 'gait disorder',
            '운동장애': 'movement disorder',
            '신경퇴행성질환': 'neurodegenerative disease',
            '심부뇌자극술': 'deep brain stimulation',
            'dbs': 'deep brain stimulation',
            
            # 치료 관련 용어
            '치료': 'treatment',
            '치료법': 'therapy',
            '치료방법': 'treatment method',
            '약물치료': 'drug therapy',
            '수술치료': 'surgical treatment',
            '물리치료': 'physical therapy',
            '재활치료': 'rehabilitation',
            '운동치료': 'exercise therapy',
            
            # 신경자극술 관련 용어 추가
            'spinal cord stimulation': 'spinal cord stimulation',
            'scs': 'spinal cord stimulation',
            '척수자극술': 'spinal cord stimulation',
            '신경자극술': 'neurostimulation',
            'neurostimulation': 'neurostimulation',
            'deep brain stimulation': 'deep brain stimulation',
            'dbs': 'deep brain stimulation',
            '심부뇌자극술': 'deep brain stimulation',
            'vagus nerve stimulation': 'vagus nerve stimulation',
            'vns': 'vagus nerve stimulation',
            '미주신경자극술': 'vagus nerve stimulation',
            'peripheral nerve stimulation': 'peripheral nerve stimulation',
            'pns': 'peripheral nerve stimulation',
            '말초신경자극술': 'peripheral nerve stimulation',
            'transcutaneous electrical nerve stimulation': 'tens',
            'tens': 'tens',
            '경피전기신경자극술': 'tens',
            
            # 통증 관련 용어
            '만성통증': 'chronic pain',
            '신경병증성통증': 'neuropathic pain',
            '요통': 'back pain',
            '목통증': 'neck pain',
            '관절통': 'joint pain',
            '두통': 'headache',
            '편두통': 'migraine',
            
            # 효능/효과 관련 용어
            '효능': 'efficacy',
            '효과': 'effectiveness',
            '효과성': 'effectiveness',
            '치료효과': 'therapeutic effect',
            '임상효과': 'clinical effect',
            '결과': 'outcome',
            '성과': 'outcome'
        }
    
    def analyze_input(self, text: str) -> List[MedicalEntity]:
        """입력 텍스트에서 의료 개체 추출"""
        entities = []
        text_lower = text.lower()
        
        # 검사 수치 패턴 분석
        entities.extend(self._extract_lab_values(text))
        
        # 질병명 추출
        entities.extend(self._extract_diseases(text))
        
        # 치료/시술 추출 (새로 추가)
        entities.extend(self._extract_treatments(text))
        
        # 혈압 패턴 (특별 처리)
        bp_pattern = r'(\d{2,3})/(\d{2,3})'
        bp_matches = re.findall(bp_pattern, text)
        for match in bp_matches:
            systolic, diastolic = int(match[0]), int(match[1])
            if 80 <= systolic <= 250 and 40 <= diastolic <= 150:  # 합리적인 혈압 범위
                entities.append(MedicalEntity(
                    text=f"{systolic}/{diastolic}",
                    entity_type='test',
                    value=systolic,  # 수축기 혈압을 주요 값으로
                    unit='mmHg',
                    normal_range=self.lab_values['bp']['normal']
                ))
        
        return entities
    
    def _extract_lab_values(self, text: str) -> List[MedicalEntity]:
        """검사 수치 추출"""
        entities = []
        
        # CA-125 특별 패턴 처리 (우선 처리 - 수치 있음)
        ca125_value_patterns = [
            r'ca\s*-?\s*125\s*:?\s*(\d+\.?\d*)',
            r'ca125\s*:?\s*(\d+\.?\d*)',
            r'ca\s+125\s*:?\s*(\d+\.?\d*)',
        ]
        
        ca125_found = False
        for pattern in ca125_value_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                try:
                    value = float(match)
                    entities.append(MedicalEntity(
                        text=f"CA-125 {value}",
                        entity_type='test',
                        value=value,
                        unit='U/mL',
                        normal_range=self.lab_values['ca125']['normal']
                    ))
                    ca125_found = True
                except ValueError:
                    continue
        
        # CA-125 언급만 있는 경우 (수치 없음)
        if not ca125_found:
            ca125_mention_patterns = [
                r'ca\s*-?\s*125',
                r'ca125',
                r'ca\s+125'
            ]
            
            for pattern in ca125_mention_patterns:
                if re.search(pattern, text.lower()):
                    entities.append(MedicalEntity(
                        text="CA-125",
                        entity_type='test',
                        value=None,
                        unit='U/mL',
                        normal_range=self.lab_values['ca125']['normal']
                    ))
                    ca125_found = True
                    break
        
        # 다른 종양 표지자들도 수치 없이 인식
        tumor_markers = {
            'cea': ['cea'],
            'afp': ['afp', 'alpha fetoprotein'],
            'psa': ['psa', 'prostate specific antigen'],
            'ca19-9': ['ca 19-9', 'ca19-9', 'ca 19 9'],
            'ca15-3': ['ca 15-3', 'ca15-3', 'ca 15 3'],
            'beta-hcg': ['beta hcg', 'beta-hcg', 'bhcg'],
            'ldh': ['ldh', 'lactate dehydrogenase']
        }
        
        for marker_key, patterns in tumor_markers.items():
            marker_found = False
            for pattern in patterns:
                if pattern in text.lower():
                    entities.append(MedicalEntity(
                        text=self.lab_values[marker_key]['name'],
                        entity_type='test',
                        value=None,
                        unit=self._extract_unit_from_normal_range(self.lab_values[marker_key]['normal']),
                        normal_range=self.lab_values[marker_key]['normal']
                    ))
                    marker_found = True
                    break
            if marker_found:
                break
        
        # 수치 패턴: 숫자 + 단위 또는 단순 숫자 (기존 로직)
        for test_key, test_info in self.lab_values.items():
            # CA-125와 종양 표지자들은 이미 처리했으므로 건너뛰기
            if test_key in ['ca125', 'ca-125', 'ca 125', 'cea', 'afp', 'psa', 'ca19-9', 'ca15-3', 'beta-hcg', 'ldh']:
                continue
                
            # 검사명 패턴 찾기
            patterns = [
                rf'{test_key}\s*:?\s*(\d+\.?\d*)',
                rf'{test_info["name"].lower()}\s*:?\s*(\d+\.?\d*)',
            ]
            
            # 한국어 검사명도 추가
            korean_names = {
                'crp': 'c반응성단백',
                'hba1c': '당화혈색소',
                'glucose': '혈당',
                'cholesterol': '콜레스테롤',
                'bp': '혈압'
            }
            
            if test_key in korean_names:
                patterns.append(rf'{korean_names[test_key]}\s*:?\s*(\d+\.?\d*)')
            
            for pattern in patterns:
                matches = re.findall(pattern, text.lower())
                for match in matches:
                    try:
                        value = float(match)
                        entities.append(MedicalEntity(
                            text=f"{test_key.upper()} {value}",
                            entity_type='test',
                            value=value,
                            unit=self._extract_unit_from_normal_range(test_info['normal']),
                            normal_range=test_info['normal']
                        ))
                    except ValueError:
                        continue
        
        return entities
    
    def _extract_diseases(self, text: str) -> List[MedicalEntity]:
        """질병명 추출 (개선된 버전)"""
        entities = []
        text_lower = text.lower()
        
        # 부분 매칭을 위한 특별 처리
        special_patterns = {
            '파킨슨': 'parkinson disease',
            '파킨슨병': 'parkinson disease',
            '알츠하이머': 'alzheimer disease',
            '치매': 'dementia',
            '당뇨': 'diabetes mellitus',
            '고혈압': 'hypertension',
            '고지혈': 'hyperlipidemia',
            '심근경색': 'myocardial infarction',
            '뇌졸중': 'stroke',
            '관절염': 'arthritis',
            '천식': 'asthma',
            '우울증': 'depression',
            '불안': 'anxiety disorder',
            '간염': 'hepatitis',
            '신부전': 'renal failure',
            '심부전': 'heart failure',
            '골다공증': 'osteoporosis',
            '난소암': 'ovarian cancer',
            '유방암': 'breast cancer',
            '폐암': 'lung cancer',
            '대장암': 'colorectal cancer',
            '위암': 'gastric cancer',
            '간암': 'liver cancer',
            '췌장암': 'pancreatic cancer',
            '전립선암': 'prostate cancer'
        }
        
        # 특별 패턴 먼저 확인 (부분 매칭)
        for korean_pattern, english_disease in special_patterns.items():
            if korean_pattern in text:
                entities.append(MedicalEntity(
                    text=korean_pattern,
                    entity_type='disease'
                ))
                break  # 첫 번째 매칭된 것만 사용
        
        # 기존 완전 매칭도 확인
        for korean_disease, english_disease in self.diseases.items():
            if korean_disease in text and korean_disease not in [e.text for e in entities]:
                entities.append(MedicalEntity(
                    text=korean_disease,
                    entity_type='disease'
                ))
            elif english_disease.lower() in text_lower and english_disease not in [e.text for e in entities]:
                entities.append(MedicalEntity(
                    text=english_disease,
                    entity_type='disease'
                ))
        
        return entities
    
    def _extract_treatments(self, text: str) -> List[MedicalEntity]:
        """치료/시술 용어 추출 (새로 추가)"""
        entities = []
        text_lower = text.lower()
        
        # 치료/시술 관련 키워드들
        treatment_keywords = {
            'spinal cord stimulation': 'treatment',
            'scs': 'treatment', 
            '척수자극술': 'treatment',
            '신경자극술': 'treatment',
            'neurostimulation': 'treatment',
            'deep brain stimulation': 'treatment',
            'dbs': 'treatment',
            '심부뇌자극술': 'treatment',
            'vagus nerve stimulation': 'treatment',
            'vns': 'treatment',
            '미주신경자극술': 'treatment',
            'peripheral nerve stimulation': 'treatment',
            'pns': 'treatment',
            '말초신경자극술': 'treatment',
            'tens': 'treatment',
            '경피전기신경자극술': 'treatment',
            '수술': 'treatment',
            '시술': 'treatment',
            '요법': 'treatment'
        }
        
        for keyword, entity_type in treatment_keywords.items():
            if keyword in text_lower:
                entities.append(MedicalEntity(
                    text=keyword,
                    entity_type=entity_type
                ))
        
        return entities
    
    def _extract_unit_from_normal_range(self, normal_range: str) -> str:
        """정상 범위에서 단위 추출"""
        unit_patterns = [
            r'(mg/dL)', r'(mg/L)', r'(g/dL)', r'(U/L)', 
            r'(mmHg)', r'(%)', r'(/μL)', r'(M/μL)'
        ]
        
        for pattern in unit_patterns:
            match = re.search(pattern, normal_range)
            if match:
                return match.group(1)
        
        return ''
    
    def generate_search_query(self, entities: List[MedicalEntity], original_text: str) -> str:
        """의료 개체를 기반으로 PubMed 검색 쿼리 생성 (최적화된 버전)"""
        query_parts = []
        
        # spinal cord stimulation 특별 처리 (최우선)
        text_lower = original_text.lower()
        if any(term in text_lower for term in ['spinal cord stimulation', 'scs', '척수자극술']):
            # 간단하고 정확한 SCS 쿼리 사용
            query_parts.append('"spinal cord stimulation"')
            
            # 효능/효과 키워드가 있으면 추가
            if any(keyword in text_lower for keyword in ['효능', '효과', 'efficacy', 'effectiveness']):
                query_parts.append('"efficacy"')
            
            # 치료법 키워드가 있으면 추가  
            if any(keyword in text_lower for keyword in ['치료', '치료법', 'treatment', 'therapy']):
                query_parts.append('"treatment"')
            
            # 간단한 쿼리로 종료
            query = ' AND '.join(query_parts)
            query += ' AND "humans"[MeSH Terms]'  # 인간 대상 연구로만 제한
            query += ' AND ("2014"[Date - Publication] : "2024"[Date - Publication])'
            return query
        
        # CA-125 및 종양 표지자 특별 처리
        if any(term in text_lower for term in ['ca 125', 'ca-125', 'ca125']):
            query_parts.append('"CA-125"')
            
            # 관련 키워드 추가
            if any(keyword in text_lower for keyword in ['정상', '범위', 'normal', 'range']):
                query_parts.append('"reference values"')
            if any(keyword in text_lower for keyword in ['높', '상승', 'elevated', 'high']):
                query_parts.append('"ovarian cancer"')
            if any(keyword in text_lower for keyword in ['기준', 'cutoff', 'threshold']):
                query_parts.append('"diagnostic"')
                
            # 간단한 쿼리로 종료
            query = ' AND '.join(query_parts)
            query += ' AND "humans"[MeSH Terms]'
            query += ' AND ("2014"[Date - Publication] : "2024"[Date - Publication])'
            return query
        
        # 다른 종양 표지자들 처리
        tumor_marker_searches = {
            'cea': '"CEA"',
            'afp': '"AFP"',
            'psa': '"PSA"',
            'ca 19-9': '"CA 19-9"',
            'ca15-3': '"CA 15-3"',
            'beta hcg': '"beta-hCG"'
        }
        
        for marker, query_term in tumor_marker_searches.items():
            if marker in text_lower:
                query_parts.append(query_term)
                query_parts.append('"tumor marker"')
                break
        
        # 다른 신경자극술 처리
        if any(term in text_lower for term in ['deep brain stimulation', 'dbs', '심부뇌자극술']):
            query_parts.append('"deep brain stimulation"')
            if any(keyword in text_lower for keyword in ['파킨슨', 'parkinson']):
                query_parts.append('"parkinson disease"')
        elif any(term in text_lower for term in ['neurostimulation', '신경자극술']):
            query_parts.append('"neurostimulation"')
            query_parts.append('"chronic pain"')
        
        # 일반적인 처리 (기존 로직)
        if not query_parts:
            # 치료/시술 추가
            treatments = [e for e in entities if e.entity_type == 'treatment']
            for treatment in treatments:
                query_parts.append(f'"{treatment.text}"')
            
            # 질병명 추가
            diseases = [e for e in entities if e.entity_type == 'disease']
            for disease in diseases:
                # 치료 관련 키워드는 이미 처리했으므로 제외
                if disease.text.lower() not in ['치료', '치료법', '치료방법', '효능', '효과', '효과성']:
                    if disease.text in self.diseases:
                        english_name = self.diseases[disease.text]
                        query_parts.append(f'"{english_name}"')
                    else:
                        query_parts.append(f'"{disease.text}"')
            
            # 검사 항목 추가
            tests = [e for e in entities if e.entity_type == 'test']
            for test in tests:
                if test.text.startswith('CA-125'):
                    query_parts.append('"CA-125"')
                    query_parts.extend(['"tumor marker"', '"ovarian cancer"'])
                elif test.text.startswith('CEA'):
                    query_parts.append('"CEA"')
                    query_parts.append('"tumor marker"')
                elif test.text.startswith('AFP'):
                    query_parts.append('"AFP"')
                    query_parts.append('"tumor marker"')
                elif test.text.startswith('PSA'):
                    query_parts.append('"PSA"')
                    query_parts.append('"prostate cancer"')
                else:
                    test_name = test.text.split()[0].lower()
                    if test_name in self.lab_values:
                        lab_info = self.lab_values[test_name]
                        query_parts.append(f'"{lab_info["name"]}"')
                        
                        # 수치가 비정상인 경우 관련 키워드 추가
                        if test.value is not None:
                            if self._is_abnormal_value(test_name, test.value):
                                query_parts.extend([f'"{kw}"' for kw in lab_info['keywords'][:2]])  # 최대 2개만
            
            # 효능/효과 키워드가 있는 경우 추가
            effectiveness_keywords = ['효능', '효과', '효과성', 'efficacy', 'effectiveness', 'outcome']
            for keyword in effectiveness_keywords:
                if keyword in text_lower and not any(keyword in qp for qp in query_parts):
                    if keyword in ['효능', '효과', '효과성']:
                        query_parts.append('"efficacy"')
                    else:
                        query_parts.append(f'"{keyword}"')
                    break
        
        # 쿼리가 없으면 원본 텍스트에서 직접 추출
        if not query_parts:
            medical_terms = self._extract_medical_terms(original_text)
            if medical_terms:
                query_parts.extend([f'"{term}"' for term in medical_terms[:2]])  # 최대 2개만
            else:
                # 최후의 수단: 기본 의료 키워드
                query_parts = ['"treatment"', '"therapy"']
        
        # 최종 쿼리 조합 (간소화)
        query = ' AND '.join(query_parts[:4])  # 최대 4개 조건만 사용
        
        # 의료 관련 필터 추가 (간소화)
        query += ' AND "humans"[MeSH Terms]'  # 인간 대상 연구로만 제한
        
        # 최근 10년 논문으로 제한
        query += ' AND ("2014"[Date - Publication] : "2024"[Date - Publication])'
        
        return query
    
    def _extract_medical_terms(self, text: str) -> List[str]:
        """텍스트에서 의료 관련 용어 추출"""
        medical_terms = []
        text_lower = text.lower()
        
        # spinal cord stimulation 우선 처리
        if 'spinal cord stimulation' in text_lower:
            medical_terms.extend(['spinal cord stimulation', 'chronic pain', 'neuropathic pain', 'pain management'])
            return medical_terms
        
        if 'scs' in text_lower and ('치료' in text_lower or '효능' in text_lower):
            medical_terms.extend(['spinal cord stimulation', 'chronic pain', 'neuropathic pain'])
            return medical_terms
            
        if '척수자극술' in text_lower:
            medical_terms.extend(['spinal cord stimulation', 'chronic pain', 'neuropathic pain'])
            return medical_terms
        
        # 기타 신경자극술
        if 'deep brain stimulation' in text_lower or 'dbs' in text_lower:
            medical_terms.extend(['deep brain stimulation', 'parkinson disease', 'movement disorder'])
            return medical_terms
            
        if 'neurostimulation' in text_lower or '신경자극술' in text_lower:
            medical_terms.extend(['neurostimulation', 'chronic pain', 'neuropathic pain'])
            return medical_terms
        
        # 일반적인 의료 용어들 (확장)
        medical_vocabulary = {
            '치료': 'treatment',
            '진단': 'diagnosis',
            '증상': 'symptoms',
            '환자': 'patient',
            '임상': 'clinical',
            '수술': 'surgery',
            '시술': 'procedure',
            '요법': 'therapy',
            '약물': 'drug',
            '투약': 'medication',
            '처방': 'prescription',
            '검사': 'examination',
            '진료': 'medical care',
            '병원': 'hospital',
            '의료': 'medical',
            '질환': 'disease',
            '질병': 'disease',
            '병증': 'syndrome',
            '증후군': 'syndrome',
            '장애': 'disorder',
            '감염': 'infection',
            '염증': 'inflammation',
            '종양': 'tumor',
            '암': 'cancer',
            '통증': 'pain',
            '아픔': 'pain',
            '열': 'fever',
            '기침': 'cough',
            '호흡': 'breathing',
            '심장': 'heart',
            '혈압': 'blood pressure',
            '혈당': 'blood glucose',
            '콜레스테롤': 'cholesterol',
            '간': 'liver',
            '신장': 'kidney',
            '폐': 'lung',
            '뇌': 'brain',
            '신경': 'nerve',
            '근육': 'muscle',
            '뼈': 'bone',
            '관절': 'joint',
            '피부': 'skin',
            '혈액': 'blood',
            '소변': 'urine',
            '변': 'stool',
            '체중': 'weight',
            '비만': 'obesity',
            '당뇨': 'diabetes',
            '고혈압': 'hypertension',
            '고지혈': 'hyperlipidemia',
            '파킨슨': 'parkinson',
            '알츠하이머': 'alzheimer',
            
            # 효능/효과 관련
            '효능': 'efficacy',
            '효과': 'effectiveness',
            '결과': 'outcome',
            '성과': 'result',
            '반응': 'response',
            '개선': 'improvement',
            '완화': 'relief',
            '감소': 'reduction',
            '증가': 'increase',
            '향상': 'enhancement',
            
            # 통증 관련 (spinal cord stimulation과 관련)
            '만성통증': 'chronic pain',
            '신경통': 'neuralgia',
            '신경병증': 'neuropathy',
            '요통': 'back pain',
            '목통증': 'neck pain',
            '두통': 'headache',
            '편두통': 'migraine',
            '관절통': 'joint pain',
            '근육통': 'muscle pain',
            '복통': 'abdominal pain',
            '흉통': 'chest pain'
        }
        
        # 텍스트에서 의료 용어 찾기
        for korean_term, english_term in medical_vocabulary.items():
            if korean_term in text_lower:
                medical_terms.append(english_term)
        
        # 영어 의료 용어도 확인
        english_medical_terms = [
            'treatment', 'therapy', 'diagnosis', 'clinical', 'patient', 'surgery',
            'medication', 'drug', 'procedure', 'examination', 'medical', 'disease',
            'syndrome', 'disorder', 'infection', 'inflammation', 'tumor', 'cancer',
            'pain', 'fever', 'chronic', 'acute', 'efficacy', 'effectiveness', 'outcome'
        ]
        
        for term in english_medical_terms:
            if term in text_lower and term not in medical_terms:
                medical_terms.append(term)
        
        return list(set(medical_terms))  # 중복 제거
    
    def _is_abnormal_value(self, test_name: str, value: float) -> bool:
        """수치가 정상 범위를 벗어나는지 확인"""
        # 간단한 임계값 기반 판단 (실제로는 더 정교한 로직 필요)
        thresholds = {
            'crp': 3.0,
            'hba1c': 5.7,
            'glucose': 100.0,
            'cholesterol': 200.0,
            'bp': 120.0  # 수축기 혈압
        }
        
        if test_name in thresholds:
            return value > thresholds[test_name]
        
        return False
    
    def interpret_values(self, entities: List[MedicalEntity]) -> List[str]:
        """수치 해석 결과 반환"""
        interpretations = []
        
        for entity in entities:
            if entity.entity_type == 'test' and entity.value is not None:
                test_name = entity.text.split()[0].lower()
                if test_name in self.lab_values:
                    lab_info = self.lab_values[test_name]
                    is_abnormal = self._is_abnormal_value(test_name, entity.value)
                    
                    status = "비정상" if is_abnormal else "정상 범위"
                    interpretation = f"{lab_info['name']}: {entity.value} ({status}, 정상: {entity.normal_range})"
                    interpretations.append(interpretation)
        
        return interpretations 