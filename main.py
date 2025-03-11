# from gui.main import main as gui_main
import latex
from gui.NiceGUI.main import ui

if __name__ == '__main__':
    # gui_main()
    # latex.albert_letter(
    #     to_name='Frau Kronhardt',
    #     to_address='Ottmar-Pohl-Platz 1',
    #     to_zip='51103',
    #     to_city='Köln',
    #     opening='Sehr geehrter Frau Kronhardt,',
    #     body='bitte nehmen Sie die Kopie des Berichts vom Krankenhaus Mara zur Kenntnis. Außer dieser '
    #          'Rehabilitationsbehandlung fanden keine weiteren Behandlungen bzgl. der Operation statt.',
    #     your_ref='44S0512871',
    #     # filename='test',
    # )
    # import cli
    # cli.main()

    pass

ui.run(title="Letter Generator", port=8080)
