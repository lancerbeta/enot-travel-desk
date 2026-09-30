"""Local Chromium evidence for the actual frozen bundle; not a WCAG audit."""
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
PAGE = ROOT / 'evidence/bundle/Путеводитель.html'
OUT = ROOT / 'evidence/browser'

OVERFLOW = '''() => [...document.querySelectorAll('body,main,section,dl,dd,dt,details,pre,figure,nav,.pair,.callout')].filter(e => e.scrollWidth > e.clientWidth + 1).map(e => ({tag:e.tagName,id:e.id,cls:e.className,client:e.clientWidth,scroll:e.scrollWidth}))'''


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    receipt={'mode':'real Chromium; exact output HTML bytes via set_content; offline; javascript disabled; file URL blocked by administrator','input_sha256':hashlib.sha256(PAGE.read_bytes()).hexdigest(),'viewports':{},'network':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        receipt['browser_version']=browser.version
        for width in (1280,390,320):
            context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=False,offline=True)
            page=context.new_page()
            page.on('request',lambda request: receipt['network'].append(request.url) if request.url.startswith(('http:','https:')) else None)
            page.set_content(PAGE.read_text(encoding='utf-8'))
            # Native details must open with keyboard, despite JS being unavailable.
            summary=page.locator('#depth-budget > summary')
            summary.focus()
            page.keyboard.press('Enter')
            assert page.locator('#depth-budget').get_attribute('open') is not None
            focus=page.evaluate('''() => ({tag:document.activeElement.tagName,outline:getComputedStyle(document.activeElement).outlineStyle})''')
            assert focus['tag']=='SUMMARY' and focus['outline']!='none',focus
            # Explicitly open every depth block for intrinsic overflow checks.
            for detail in page.locator('details').all():
                if detail.get_attribute('open') is None:
                    detail.locator('summary').focus();page.keyboard.press('Enter')
            for photo in page.locator('img').all():photo.scroll_into_view_if_needed()
            images=page.evaluate('''() => [...document.images].map(i=>({src:i.src.slice(0,23),complete:i.complete,width:i.naturalWidth,height:i.naturalHeight,alt:i.alt}))''')
            assert len(images)==4 and all(i['complete'] and i['width']>0 and i['alt'] for i in images),images
            page.wait_for_timeout(100)
            overflow=page.evaluate(OVERFLOW)
            assert overflow==[],overflow
            assert page.evaluate('document.body.scrollWidth<=innerWidth'),width
            receipt['viewports'][str(width)]={'overflow':overflow,'images':images,'keyboard_focus':focus,'all_depth_open':True}
            if width==1280:
                page.evaluate('window.scrollTo(0,0)');page.screenshot(path=str(OUT/'desktop-hero.png'))
            if width==390:
                page.evaluate('(el)=>window.scrollTo(0,el.getBoundingClientRect().top+scrollY-330)',page.locator('#hotel .callout').element_handle());page.screenshot(path=str(OUT/'mobile-hotel.png'))
                page.evaluate('(el)=>window.scrollTo(0,el.getBoundingClientRect().top+scrollY-24)',page.locator('#depth-budget').element_handle());page.screenshot(path=str(OUT/'mobile-budget.png'))
                page.emulate_media(media='print')
                assert page.locator('#depth-sources').is_visible()
                page.pdf(path=str(OUT/'print-sample.pdf'),format='A4',print_background=True)
                receipt['print']='all depth open; print screenshot/PDF generated; inspect sample separately'
            context.close()
        browser.close()
    assert receipt['network']==[],receipt['network']
    (OUT/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'viewports':list(receipt['viewports']),'internal_overflow':0,'loaded_photos':4,'network_requests':len(receipt['network']),'keyboard':'native summary Enter/focus visible','no_js':True},ensure_ascii=False))


if __name__=='__main__':main()
