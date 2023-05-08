# Generated by Django 3.2.8 on 2022-05-20 20:26

from django.db import migrations
from django.db import transaction
from sportdiag.models import Survey as _Survey
from sportdiag.models import Question as _Question
from bp.utils.migrations import integer_sequence

app_name = 'sportdiag'
survey_name = "Dotazník živosti pohybové imaginace – 2"


@transaction.atomic
def add_vmiq_survey(apps, schema_editor):
    Survey = apps.get_model(app_name, 'Survey')
    survey = Survey.objects.create(
        name=survey_name,
        description="""Vividness of Movement Imagery Questionnaire (Roberts et al., 2008) je celosvětově jeden
         z nejčastěji používaných dotazníků pohybové imaginace. Již samotný název metody poukazuje na povahu 
         měřeného. Jako základní hodnotící ukazatel je zde vybrána živost (vividness), kterou můžeme též rozumět jako 
         reálnost představ. Tzn. do jaké míry je vytvářená představa podobná reálnému výkonu. Dotazník obsahuje 12 
         pohybových úkolů (např. běh z kopce, skok z vysoké zídky…). Tyto pohyby nejsou sportovně specifické. 
         Úkolem probanda je ohodnotit, nakolik živá je každá z těchto představ na stupnici od 1 do 5. VMIQ-2 je 
         navržen tak, aby měřil vizuální a kinestetickou imaginaci těchto pohybů. Proto jsou tyto pohybové úkoly 
         imaginovány zvlášť pro vizuální představu a zvlášť pro kinestetickou. Vizuální imaginace je navíc rozdělena
          na interní a externí. Celkově tedy proband hodností 3x12 úkolů.""",
        instructions="""Pohybová imaginace souvisí se schopností vybavit si pohyb. Cílem tohoto dotazníku je zjistit, 
        nakolik je vaše pohybová imaginace reálná. Otázky v dotazníku jsou kladeny tak, aby ve vaší mysli navodily 
        určitou představu. Vaším úkolem je ohodnotit, nakolik živá je každá z těchto představ na stupnici od 1 do 5. 
        U každé otázky zakroužkujte příslušné číslo v připravených kolonkách. V prvním sloupci jsou představy, 
        v nichž jako pozorovatel zvenčí sledujete, jak provádíte daný pohyb (externí vizuální imaginace) a v druhém 
        sloupci představy vnitřní, v nichž provádíte pohyb a přitom se díváte vlastníma očima (interní vizuální 
        imaginace). Třetí sloupec obsahuje představu fyzických pocitů, které provádění pohybu provázejí (kinestetická 
        imaginace). Snažte se ke každému úkolu přistupovat zvlášť, nezávisle na tom, jak jste zodpověděli ostatní 
        otázky. Nejprve zodpovězte všechny otázky z externí vizuální perspektivy, pak se vraťte na začátek 
        dotazníku a zodpovězte otázky z interní vizuální perspektivy. Nakonec se opět vraťte na začátek
         a zodpovězte otázky z hlediska pocitů. Hodnocení těchto tří hledisek u jednoho úkolu se může lišit. 
         U všech úkolů prosím mějte ZAVŘENÉ OČI.""",
        is_published=True,
        type=_Survey.VMIQ2,
    )
    # add survey categories
    Category = apps.get_model(app_name, 'Category')
    categories = [
        Category(name="Externí zraková představivost",
                 survey=survey,
                 description="""Externí zraková představivost  je definována jako zraková představa sebe sama ve třetí osobě. 
                 Odkazuje na to, aby si účastníci představovali jednotlivé položky pohybů, jako kdyby se dívali na sebe, 
                 jak daný pohyb provádí. Tzn. ne ze svého těla, ale jako by se sledovali na filmovém plátně."""
                 ),
        Category(name="Interní zraková představivost",
                 survey=survey,
                 description="""Interní zraková představivost je definována jako zraková představa sebe sama v první
                  osobě. Jako byste měli na hlavě kameru, uvidíte pouze to, co je vidět, když právě provádíte určitou 
                  dovednost. Protože vnitřní imaginace pochází ze zorného pole nás samých, obrazy zdůrazňují pocit pohybu. 
                  Tento pocit pohybu úzce souvisí s další složkou dotazníku a tou je kinestetická modalita."""
                 ),
        Category(name="Kinestetická (pohybově pocitová) představivost",
                 survey=survey,
                 description="""Kinestetická (pohybově pocitová) představivost je definována jako představy pocitů 
                 doprovázejících pohyb. Kinestetická imaginace odkazuje probandy na to, aby se v představách zaměřili na
                  pocity ve svém těle, které doprovázejí jednotlivé pohyby. V podstatě je kinestetický smysl pocit 
                  našeho těla, když se pohybuje v různých polohách. Kinestetický smysl je u sportovců velmi důležitý, 
                  protože zahrnuje pocit pozice těla nebo pohyb, který začíná od stimulace nervového zakončení ve svalech, 
                  kloubech a šlachách."""
                 ),
    ]
    for category in categories:
        category.save()
    QuestionGroup = apps.get_model(app_name, 'QuestionGroup')
    question_groups = [
        QuestionGroup(
            name="Externí vizuální imaginace",
            description="Jako pozorovatel zvenčí sledujete, jak pohyb provádíte.",
            instructions="Vybavte si každou činnost a vyberte odpověď podle toho, jak je vaše představa jasná a reálná.",
            survey=survey,
        ),
        QuestionGroup(
            name="Interní vizuální imaginace",
            description="Provádíte pohyb a přitom se díváte vlastníma očima.",
            instructions="Vybavte si každou činnost a vyberte odpověď podle toho, jak je vaše představa jasná a reálná.",
            survey=survey,
        ),
        QuestionGroup(
            name="Kinestetická imaginace",
            description="Pocity, které provázejí provádění pohybu.",
            instructions="Vybavte si každou činnost a vyberte odpověď podle toho, jak je vaše představa jasná a reálná.",
            survey=survey,
        ),
    ]
    # QuestionGroup.objects.bulk_create(question_groups) # bulk create does not invoke save()
    for group in question_groups:
        group.save()
    # add survey questions
    Question = apps.get_model(app_name, 'Question')
    choices = "Dokonale jasná a reálná (odpovídající skutečnému vidění a pocitu z pohybu), Jasná a celkem reálná, Středně jasná a reálná, Nejasná a neurčitá, Vůbec žádná představa (na danou dovednost pouze myslíte)"
    scores = "1,2,3,4,5"
    number = integer_sequence(100)
    order_number = integer_sequence(100)
    questions = [
        # no category questions
        Question(text="Sport",
                 number=0,
                 order=next(order_number),
                 required=True,
                 type=_Question.SHORT_TEXT,
                 survey=survey,
                 scores="0"),
        Question(text="Současná úroveň, na které provozujete svůj sport",
                 number=0,
                 order=next(order_number),
                 required=True,
                 type=_Question.RADIO,
                 survey=survey,
                 choices="Regionální úroveň, Celonárodní úroveň, Mezinárodní reprezentace, Svůj sport aktivně neprovozuji",
                 scores="0,0,0,0"),
        Question(text="Nejvyšší úroveň, na které jste provozoval/a svůj sport",
                 number=0,
                 order=next(order_number),
                 required=True,
                 type=_Question.RADIO,
                 survey=survey,
                 choices="Regionální úroveň, Celonárodní úroveň, Mezinárodní reprezentace",
                 scores="0,0,0"),
        Question(text="Nejvyšší stupeň dokončeného vzdělání",
                 number=0,
                 order=next(order_number),
                 required=True,
                 type=_Question.SELECT,
                 survey=survey,
                 choices="Základní, Střední, Vyšší odborné, Vysokoškolské",
                 scores="0,0,0,0"),
    ]
    # categorized questions
    questions_texts = [
        "Chůze",
        "Běh",
        "Kopnutí do kamínku",
        "Ohnutí se pro minci",
        "Běh nahoru po schodech",
        "Odskok stranou",
        "Hod kamenem do vody",
        "Vykopnutí míče do vzduchu",
        "Běh z kopce",
        "Jízda na kole",
        "Zhoupnutí se na provaze",
        "Seskok z vysoké zdi",
    ]
    for i in range(0, 3):
        for question_text in questions_texts:
            questions.append(
                Question(text=question_text,
                         number=next(number),
                         order=next(order_number),
                         required=True,
                         type=_Question.RADIO,
                         survey=survey,
                         choices=choices,
                         scores=scores,
                         category=categories[i],
                         group=question_groups[i],
                         ),
            )
    Question.objects.bulk_create(questions)


@transaction.atomic
def revert_vmiq_survey(apps, schema_editor):
    Survey = apps.get_model(app_name, 'Survey')
    survey = Survey.objects.get(name=survey_name)
    if survey:
        survey.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('sportdiag', '0010_demo_data_pcdeq_survey'),
    ]

    operations = [
        migrations.RunPython(add_vmiq_survey, reverse_code=revert_vmiq_survey),
    ]
