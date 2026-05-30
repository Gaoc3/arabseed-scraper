#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Command-Line Interface (CLI) for ArabSeed Scraper
------------------------------------------------
Provides a beautiful, interactive CLI to search and extract links.
"""

import sys
from .scraper import ArabSeedAPI

# Configure UTF-8 output to support Arabic characters in all terminals
sys.stdout.reconfigure(encoding='utf-8')

# Try importing rich for beautiful terminal styling; fall back gracefully if missing
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.prompt import Prompt, IntPrompt
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

def print_rich_header(console: Console, api: ArabSeedAPI):
    """Draws a premium header panel on terminals that support Rich."""
    header_text = Text()
    header_text.append("عرب سيد ", style="bold red")
    header_text.append("ArabSeed Downloader & Link Extractor 🚀\n", style="bold white")
    header_text.append(f"Mirror API: {api.base_url}", style="dim cyan")
    
    console.print(
        Panel(
            header_text,
            box=box.ROUNDED,
            border_style="red",
            title="[bold white]Antigravity Web Scraper[/bold white]",
            title_align="center"
        )
    )

def run_cli():
    """Main CLI execution loop."""
    # Fallback if Rich is not installed
    if not HAS_RICH:
        print("="*60)
        print(" ArabSeed Downloader & Link Extractor (Antigravity)")
        print("="*60)
        
        query = input("🔍 أدخل اسم الفلم، المسلسل أو الموسيقى للبحث: ")
        api = ArabSeedAPI()
        print("⏳ جاري البحث في عرب سيد...")
        try:
            results = api.search(query)
            if not results:
                print("❌ لم يتم العثور على نتائج.")
                return
                
            for idx, item in enumerate(results):
                print(f"[{idx+1}] {item['title']} | الجودة: {item['quality']} | النوع: {item['type']}")
                
            choice = int(input("\n👉 اختر رقم العنصر لرؤية روابط التحميل: ")) - 1
            if choice < 0 or choice >= len(results):
                print("❌ اختيار غير صحيح.")
                return
                
            selected = results[choice]
            print(f"\n⏳ جاري تحميل تفاصيل: {selected['title']}...")
            details = api.get_details(selected['url'])
            
            target_url = selected['url']
            if details['is_series']:
                print("\n📦 هذا العنصر مسلسل. قائمة الحلقات المتوفرة:")
                for ep_idx, ep in enumerate(details['episodes']):
                    active_indicator = " ⭐" if ep['active'] else ""
                    print(f"  [{ep_idx+1}] {ep['title']}{active_indicator}")
                
                ep_choice = int(input("\n👉 اختر رقم الحلقة للتحميل: ")) - 1
                if ep_choice < 0 or ep_choice >= len(details['episodes']):
                    print("❌ اختيار غير صحيح.")
                    return
                target_url = details['episodes'][ep_choice]['url']
                print(f"⏳ جاري تحميل الحلقة: {details['episodes'][ep_choice]['title']}...")
                
            print("\n⏳ جاري استخراج وفك تشفير روابط المشاهدة والتحميل المباشرة...")
            watch_links = api.get_watch_links(target_url)
            links = api.get_download_links(target_url)
            
            if watch_links:
                print("\n📺 روابط المشاهدة المباشرة (بث مباشر):")
                print("="*80)
                for w_idx, w in enumerate(watch_links):
                    print(f"[{w_idx+1}] 🖥️ السيرفر: {w['server']}")
                    print(f"    🔗 رابط التشغيل: {w['direct_link']}")
                    print("-" * 80)
            else:
                print("\n⚠️ لا توجد روابط بث مباشر متوفرة حالياً لهذا العنصر.")
                
            if links:
                print("\n📥 روابط التحميل المباشرة والبديلة:")
                print("="*80)
                for l_idx, l in enumerate(links):
                    print(f"[{l_idx+1}] 🖥️ السيرفر: {l['server']} | الجودة: {l['quality']} | الحجم: {l['size']}")
                    print(f"    🔗 رابط التحميل: {l['direct_link']}")
                    print("-" * 80)
            else:
                print("\n❌ لم يتم العثور على روابط تحميل متوفرة لهذا العنصر.")
                
        except Exception as e:
            print("❌ حدث خطأ:", e)
        return

    # Rich Enabled Console
    console = Console()
    api = ArabSeedAPI()
    
    # Mirror Check with spinner
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        task = progress.add_task(description="[cyan]جاري الاتصال بسيرفر عرب سيد والتحقق من المرايا...[/cyan]", total=None)
        api.auto_fallback_mirror()
        
    print_rich_header(console, api)
    
    # Get Search Term
    query = Prompt.ask("[bold yellow]🔍 أدخل اسم الفلم، المسلسل، أو الموسيقى للبحث[/bold yellow]")
    if not query.strip():
        console.print("[bold red]❌ لا يمكن للبحث أن يكون فارغاً.[/bold red]")
        return
        
    # Run Search with rich spinner
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        progress.add_task(description="[bold green]🔎 جاري البحث وجلب النتائج من قاعدة البيانات...[/bold green]", total=None)
        try:
            results = api.search(query)
        except Exception as e:
            console.print(f"[bold red]❌ فشل البحث: {e}[/bold red]")
            return
            
    if not results:
        console.print("[bold red]❌ لم يتم العثور على أي نتائج تطابق بحثك.[/bold red]")
        return
        
    # Render Search Table
    table = Table(title=f"📺 نتائج البحث عن: '{query}'", box=box.HEAVY_EDGE, border_style="red")
    table.add_column("الرقم", justify="center", style="cyan", no_wrap=True)
    table.add_column("الاسم (العنوان)", style="white")
    table.add_column("النوع", style="magenta")
    table.add_column("الجودة", style="green")
    table.add_column("التقييم ⭐", style="yellow", justify="center")
    
    for idx, item in enumerate(results):
        table.add_row(
            str(idx + 1),
            item["title"],
            item["type"],
            item["quality"],
            item["rating"]
        )
        
    console.print(table)
    
    # Let user select
    choice = IntPrompt.ask(
        "\n[bold yellow]👉 اختر رقم العنصر لمشاهدة تفاصيله[/bold yellow]",
        choices=[str(x) for x in range(1, len(results) + 1)]
    ) - 1
    
    selected = results[choice]
    
    # Get details with loader
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        progress.add_task(description=f"[bold green]⏳ جاري تحليل صفحة التفاصيل واستخراج الحلقات...[/bold green]", total=None)
        try:
            details = api.get_details(selected["url"])
        except Exception as e:
            console.print(f"[bold red]❌ فشل جلب التفاصيل: {e}[/bold red]")
            return
            
    # Print Item Panel
    console.print(
        Panel(
            f"[bold cyan]القصة / التفاصيل:[/bold cyan]\n{details['description']}",
            title=f"[bold white]{details['title']}[/bold white]",
            border_style="magenta",
            box=box.ROUNDED
        )
    )
    
    target_url = selected["url"]
    
    # Handle Series / Episodes selection
    if details["is_series"]:
        episodes = details["episodes"]
        ep_table = Table(title="📦 حلقات الموسم المتوفرة", box=box.SIMPLE_HEAD, border_style="magenta")
        ep_table.add_column("الرقم", justify="center", style="cyan")
        ep_table.add_column("اسم الحلقة", style="white")
        ep_table.add_column("الحالة", style="yellow")
        
        for ep_idx, ep in enumerate(episodes):
            status = "[bold green]الحلقة الحالية[/bold green]" if ep["active"] else "جاهزة للتحميل"
            ep_table.add_row(str(ep_idx + 1), ep["title"], status)
            
        console.print(ep_table)
        
        ep_choice = IntPrompt.ask(
            "\n[bold yellow]👉 اختر رقم الحلقة التي تريد تحميلها[/bold yellow]",
            choices=[str(x) for x in range(1, len(episodes) + 1)]
        ) - 1
        
        target_url = episodes[ep_choice]["url"]
        selected_ep_title = episodes[ep_choice]["title"]
        console.print(f"[bold green]⏳ تم اختيار: {selected_ep_title}... جاري جلب صفحة التحميل...[/bold green]")
        
    # Get download & watch links with loader
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        progress.add_task(description="[bold green]🔓 جاري فك التشفير وتوليد روابط المشاهدة والتحميل المباشرة...[/bold green]", total=None)
        try:
            watch_links = api.get_watch_links(target_url)
            links = api.get_download_links(target_url)
        except Exception as e:
            console.print(f"[bold red]❌ فشل جلب الروابط: {e}[/bold red]")
            return
            
    # Show Watch Links Table
    if watch_links:
        watch_table = Table(title="📺 روابط المشاهدة المباشرة (البث المباشر)", box=box.DOUBLE_EDGE, border_style="magenta")
        watch_table.add_column("الرقم", justify="center", style="cyan")
        watch_table.add_column("سيرفر البث", style="magenta", bold=True)
        watch_table.add_column("رابط التشغيل الفوري", style="white", overflow="ellipsis")
        
        for w_idx, w in enumerate(watch_links):
            watch_table.add_row(
                str(w_idx + 1),
                w["server"],
                w["direct_link"]
            )
        console.print(watch_table)
    else:
        console.print("[bold yellow]⚠️ لا توجد سيرفرات بث مباشر متوفرة حالياً لهذا العنصر.[/bold yellow]")
        
    # Show Download Links Table
    if links:
        dl_table = Table(title="📥 روابط التحميل المباشرة والبديلة (مفكوكة التشفير)", box=box.DOUBLE_EDGE, border_style="green")
        dl_table.add_column("الرقم", justify="center", style="cyan")
        dl_table.add_column("اسم السيرفر", style="magenta", bold=True)
        dl_table.add_column("الجودة", style="green", justify="center")
        dl_table.add_column("الحجم", style="yellow", justify="center")
        dl_table.add_column("الرابط المباشر للتحميل الفوري", style="white", overflow="ellipsis")
        
        for l_idx, l in enumerate(links):
            dl_table.add_row(
                str(l_idx + 1),
                l["server"],
                l["quality"],
                l["size"],
                l["direct_link"]
            )
        console.print(dl_table)
    else:
        console.print("[bold red]❌ لم يتم العثور على أي سيرفرات تحميل نشطة لهذا العنصر حالياً.[/bold red]")
    
    console.print("\n[bold green]💡 نصيحة: يمكنك نسخ الرابط مباشرة واستخدامه في برنامج التحميل المفضل لديك (مثل IDM أو wget).[/bold green]\n")

if __name__ == "__main__":
    run_cli()
