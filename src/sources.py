"""
Configuracao das 50 principais fontes de noticias, blogs tecnicos e portais de arquitetura/IA.
"""

CURATED_SOURCES = [
    # 1. Blogs Pessoais, Criadores & Opinião Forte
    {"name": "AkitaOnRails (Fabio Akita)", "url": "https://akitaonrails.com/feed.xml", "category": "Opiniao & Carreira"},
    {"name": "Martin Fowler", "url": "https://martinfowler.com/feed.atom", "category": "Arquitetura"},
    {"name": "The Pragmatic Engineer (Gergely Orosz)", "url": "https://newsletter.pragmaticengineer.com/feed", "category": "Opiniao & Carreira"},
    {"name": "Julia Evans (jvns.ca)", "url": "https://jvns.ca/atom.xml", "category": "Sistemas & Low-Level"},
    {"name": "Overreacted (Dan Abramov)", "url": "https://overreacted.io/rss.xml", "category": "Frontend"},
    {"name": "Joel on Software (Joel Spolsky)", "url": "https://www.joelonsoftware.com/feed/", "category": "Opiniao & Engenharia"},
    {"name": "Architect Elevator (Gregor Hohpe)", "url": "https://architectelevator.com/feed.xml", "category": "Arquitetura"},
    {"name": "Chip Huyen Blog", "url": "https://huyenchip.com/feed.xml", "category": "IA & ML Engineering"},
    {"name": "Lilian Weng Blog", "url": "https://lilianweng.github.io/feed.xml", "category": "IA & Pesquisa"},
    {"name": "The Algorithmic Bridge (Alberto Romero)", "url": "https://thealgorithmicbridge.substack.com/feed", "category": "IA & Futuro"},

    # 2. Inteligência Artificial, LLMs & ML Engineering
    {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml", "category": "IA & Open Source"},
    {"name": "Latent Space", "url": "https://www.latent.space/feed", "category": "IA & AI Engineering"},
    {"name": "OpenAI Blog", "url": "https://openai.com/news/rss.xml", "category": "IA & Pesquisa"},
    {"name": "Google DeepMind Blog", "url": "https://deepmind.google/blog/rss.xml", "category": "IA & Pesquisa"},
    {"name": "LangChain Blog", "url": "https://blog.langchain.dev/rss/", "category": "IA & Agentes"},
    {"name": "Towards Data Science", "url": "https://towardsdatascience.com/feed", "category": "Data Science & ML"},
    {"name": "LlamaIndex Blog", "url": "https://www.llamaindex.ai/blog/rss.xml", "category": "IA & RAG"},
    {"name": "AI Snake Oil", "url": "https://www.aisnakeoil.com/feed", "category": "IA & Analise"},
    {"name": "Jay Alammar Blog", "url": "https://jalammar.github.io/feed.xml", "category": "IA & Didatica"},
    {"name": "MarkTechPost", "url": "https://www.marktechpost.com/feed/", "category": "IA & Papers"},

    # 3. Engenharia de Big Techs (Engineering Blogs)
    {"name": "Netflix TechBlog", "url": "https://netflixtechblog.com/feed", "category": "Engenharia & Escala"},
    {"name": "GitHub Engineering", "url": "https://github.blog/category/engineering/feed/", "category": "Engenharia & Infra"},
    {"name": "Cloudflare Blog", "url": "https://blog.cloudflare.com/rss/", "category": "Infra & Edge"},
    {"name": "Uber Engineering Blog", "url": "https://www.uber.com/blog/engineering/rss/", "category": "Engenharia & Escala"},
    {"name": "Discord Engineering", "url": "https://discord.com/blog/rss.xml", "category": "Engenharia & Banco de Dados"},
    {"name": "Spotify Engineering", "url": "https://engineering.atspotify.com/feed/", "category": "Engenharia & Sistemas"},
    {"name": "Stripe Engineering", "url": "https://stripe.com/blog/feed.rss", "category": "Engenharia & APIs"},
    {"name": "AWS Architecture Blog", "url": "https://aws.amazon.com/blogs/architecture/feed/", "category": "Arquitetura & Cloud"},
    {"name": "Canva Engineering", "url": "https://canva.dev/blog/engineering/feed.xml", "category": "Frontend & Performance"},
    {"name": "DoorDash Engineering", "url": "https://doordash.engineering/feed/", "category": "Engenharia & Logistica"},

    # 4. Portais & Portais de Arquitetura de Software
    {"name": "InfoQ", "url": "https://feed.infoq.com/", "category": "Arquitetura & Software"},
    {"name": "Better Stack Community", "url": "https://betterstack.com/community/rss.xml", "category": "DevOps & Monitoramento"},
    {"name": "Architecture Notes", "url": "https://architecturenotes.co/rss/", "category": "Arquitetura"},
    {"name": "The New Stack", "url": "https://thenewstack.io/feed/", "category": "Cloud Native & DevTools"},
    {"name": "DZone", "url": "https://dzone.com/feed/frontpage/rss", "category": "Desenvolvimento"},
    {"name": "HackerNoon", "url": "https://hackernoon.com/feed", "category": "Desenvolvimento & Tech"},
    {"name": "TLDR Tech", "url": "https://tldr.tech/tech/feed", "category": "Noticias & Curadoria"},
    {"name": "Dev.to", "url": "https://dev.to/feed", "category": "Comunidade Dev"},
    {"name": "Hashnode", "url": "https://hashnode.com/feed", "category": "Comunidade Dev"},
    {"name": "Red Hat Developer Blog", "url": "https://developers.redhat.com/blog/feed", "category": "Open Source & Linux"},

    # 5. Canais e Conteúdo em Português (Brasil)
    {"name": "TabNews", "url": "https://www.tabnews.com.br/recentes/rss", "category": "Comunidade BR"},
    {"name": "Manual do Usuário (Rodrigo Ghedin)", "url": "https://manualdousuario.net/feed/", "category": "Jornalismo & Tech BR"},
    {"name": "Filipe Deschamps Newsletter", "url": "https://filipedeschamps.com.br/newsletter", "category": "Noticias BR"},
    {"name": "BrazilJS", "url": "https://braziljs.org/blog/feed/", "category": "Web & JS BR"},
    {"name": "Blog do Diego Eis", "url": "https://diegoeis.com/feed/", "category": "Gestao & Tech BR"},
    {"name": "iMasters", "url": "https://imasters.com.br/feed", "category": "Portal Dev BR"},
    {"name": "Blog da Zup Innovation", "url": "https://zup.com.br/blog/feed", "category": "Arquitetura BR"},
    {"name": "Ezequiel Lanza Medium", "url": "https://medium.com/feed/@ezequiellanza", "category": "IA & Open Source BR"},
    {"name": "Pagar.me Stone Tech Blog", "url": "https://pagar.me/blog/feed/", "category": "Backend BR"},
    {"name": "Hubspot Mercado Dev BR", "url": "https://blog.hubspot.br/feed", "category": "Mercado BR"},
]
