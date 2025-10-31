import streamlit as st

def main():
    st.title("BUA‑berekening tool")

    st.header("Selecteer categorieën")
    categorie_auto = st.checkbox("Auto van de zaak")
    categorie_kantine = st.checkbox("Kantineregeling")
    categorie_relatie = st.checkbox("Relatiegeschenken / overige personeelsvoorzieningen")

    if categorie_auto:
        st.subheader("Auto van de zaak")
        cataloguswaarde = st.number_input("Cataloguswaarde auto (incl. btw en BPM)", min_value=0.0, step=100.0)
        eigen_bijdrage = st.number_input("Eigen bijdrage werknemer", min_value=0.0, step=100.0)
        # etc …

    if categorie_kantine:
        st.subheader("Kantineregeling")
        inkoop_spijzen = st.number_input("Inkoop spijzen & dranken excl. btw", min_value=0.0, step=100.0)
        omzet_personeel = st.number_input("Werkelijke omzet personeel incl. btw", min_value=0.0, step=100.0)
        aantal_werknemers = st.number_input("Aantal werknemers", min_value=1, step=1)
        # etc …

    if categorie_relatie:
        st.subheader("Relatiegeschenken / overige")
        totale_kosten_excl_btw = st.number_input("Totale aanschaf-/voortbrengingskosten excl. btw", min_value=0.0, step=100.0)
        aantal_begunstigden = st.number_input("Aantal begunstigden", min_value=1, step=1)
        # etc …

    if st.button("Bereken"):
        # hier logica om te berekenen
        st.write("Hier komt het berekeningsresultaat …")

if __name__ == "__main__":
    main()
