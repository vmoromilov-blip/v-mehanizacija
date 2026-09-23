from datetime import datetime

def izracunaj_smenski_turnus(start_str, turnus_tip, smena, trenutni_dt):
    try:
        start_dt = datetime.strptime(str(start_str).strip(), '%d.%m.%Y').date()
        if trenutni_dt >= start_dt:
            razlika_dana = (trenutni_dt - start_dt).days
            
            # Ako je turnus 1 - čovek radi svaki dan bez pauze
            if str(turnus_tip).strip() == '1':
                return True
                
            # Ako je turnus 5 - ritam 5 dana rada, 5 dana odmora
            elif str(turnus_tip).strip() == '5':
                ciklus = razlika_dana % 10
                if str(smena).strip().upper() == 'A':
                    return 0 <= ciklus < 5
                elif str(smena).strip().upper() == 'B':
                    return 5 <= ciklus < 10
    except:
        pass
    return False
