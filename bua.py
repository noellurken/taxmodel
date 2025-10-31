import streamlit as st

st.title("BUA-berekening tool")

st.markdown("""
Deze app berekent de BUA-btw-correctie voor kantine, personeelsvoorzieningen en relatiegeschenken.
De correctie wordt alleen toegepast als de totale kosten per begunstigde de drempel van €227 overschrijden.
""")

# Definieer groepen
st.header("Definieer groepen werknemers")
groepen = []
aantal_groepen = st.number_input("Aantal groepen werknemers", min_value=1, step=1)

for i in range(aantal_groepen):
    st.subheader(f"Groep {i+1}")
    naam = st.text_input(f"Naam groep {i+1}", value=f"Groep {i+1}")
    
    # Kosten per categorie
    kantine = st.number_input(f"Kost kantine (excl. btw) voor {naam}", min_value=0.0, step=10.0)
    personeelsvoorziening = st.number_input(f"Kost personeelsvoorzieningen (excl. btw) voor {naam}", min_value=0.0, step=10.0)
    relatiegeschenken = st.number_input(f"Kost relatiegeschenken (excl. btw) voor {naam}", min_value=0.0, step=10.0)
    
    begunstigden = st.number_input(f"Aantal begunstigden in {naam}", min_value=1, step=1)
    
    groepen.append({
        "naam": naam,
        "kantine": kantine,
        "personeelsvoorziening": personeelsvoorziening,
        "relatiegeschenken": relatiegeschenken,
        "begunstigden": begunstigden
    })

# Berekening
if st.button("Bereken BUA-correctie"):
    drempel = 227.0
    btw_tarief = 0.21  # standaard 21%, kan worden aangepast
    totaal_correctie = 0.0
    
    st.header("Resultaten per groep")
    for g in groepen:
        totaal_kosten = g["kantine"] + g["personeelsvoorziening"] + g["relatiegeschenken"]
        overschrijding = max(totaal_kosten - drempel * g["begunstigden"], 0)
        correctie = overschrijding * btw_tarief
        totaal_correctie += correctie
        
        st.write(f"**{g['naam']}**")
        st.write(f"Totale kosten excl. btw: €{totaal_kosten:.2f}")
        st.write(f"Drempel overschreden: €{overschrijding:.2f}")
        st.write(f"Te corrigeren btw: €{correctie:.2f}")
        st.write("---")
    
    st.subheader(f"Totaal BUA-btw-correctie: €{totaal_correctie:.2f}")
