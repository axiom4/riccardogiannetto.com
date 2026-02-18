from django.core.management.base import BaseCommand
from django.conf import settings
from gallery.models import ImageGallery
from blog.models import Post, Page
import os
from datetime import datetime


class Command(BaseCommand):
    help = 'Generates sitemap.xml for the website'

    def handle(self, *args, **options):
        base_url = 'https://www.riccardogiannetto.com'
        current_date_iso = datetime.now().strftime('%Y-%m-%d')

        # Start XML structure
        urlset = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        ]

        # Add Root
        urlset.append(
            f'  <url><loc>{base_url}/</loc><lastmod>{current_date_iso}</lastmod><changefreq>daily</changefreq><priority>1.0</priority></url>')

        # Add Static Pages like Map
        urlset.append(
            f'  <url><loc>{base_url}/map</loc><lastmod>{current_date_iso}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>')

        # Add Gallery Images
        images = ImageGallery.objects.all().order_by('-updated_at')
        if not images.exists():
            self.stdout.write(self.style.WARNING("No images found"))

        count_images = 0
        for image in images:
            # Format date: YYYY-MM-DD
            lastmod = image.updated_at.strftime(
                '%Y-%m-%d') if image.updated_at else current_date_iso

            # Using ID as per Angular route configuration (p/:id)
            loc = f'{base_url}/p/{image.id}'

            urlset.append(
                f'  <url>\n'
                f'    <loc>{loc}</loc>\n'
                f'    <lastmod>{lastmod}</lastmod>\n'
                f'    <changefreq>monthly</changefreq>\n'
                f'    <priority>0.6</priority>\n'
                f'  </url>'
            )
            count_images += 1

        # Add Blog Posts
        posts = Post.objects.all().order_by('-updated_at')
        count_posts = 0
        for post in posts:
            lastmod = post.updated_at.strftime(
                '%Y-%m-%d') if post.updated_at else current_date_iso
            loc = f'{base_url}/blog/{post.id}'

            urlset.append(
                f'  <url>\n'
                f'    <loc>{loc}</loc>\n'
                f'    <lastmod>{lastmod}</lastmod>\n'
                f'    <changefreq>weekly</changefreq>\n'
                f'    <priority>0.7</priority>\n'
                f'  </url>'
            )
            count_posts += 1

        # Add Static Pages (managed content pages)
        pages = Page.objects.all()
        count_pages = 0
        for page in pages:
            lastmod = page.updated_at.strftime(
                '%Y-%m-%d') if page.updated_at else current_date_iso
            loc = f'{base_url}/pages/{page.tag}'

            urlset.append(
                f'  <url>\n'
                f'    <loc>{loc}</loc>\n'
                f'    <lastmod>{lastmod}</lastmod>\n'
                f'    <changefreq>monthly</changefreq>\n'
                f'    <priority>0.5</priority>\n'
                f'  </url>'
            )
            count_pages += 1

        # Close XML structure
        urlset.append('</urlset>')

        # Define output path: rg_api/ -> ../rg_web/src/sitemap.xml
        # settings.BASE_DIR is usually the project root where manage.py is, or inner folder.
        # Assuming typical Django structure where settings.BASE_DIR points to project root.
        # If settings.BASE_DIR is .../rg_api/rg_api/ then .parent.parent is .../rg/
        # Check settings.py first line previously read: BASE_DIR = Path(__file__).resolve().parent.parent
        # This points to .../rg_api/
        # We need to go up one level to .../rg/ then into rg_web/src/

        output_dir = settings.BASE_DIR.parent / 'rg_web' / 'src'
        output_file = output_dir / 'sitemap.xml'

        try:
            if not output_dir.exists():
                self.stdout.write(self.style.WARNING(
                    f'Directory {output_dir} does not exist. Creating it if possible or failing.'))
                # Typically we don't create src folder, it should exist.

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(urlset))

            self.stdout.write(self.style.SUCCESS(
                f'Successfully generated sitemap at {output_file}'))
            self.stdout.write(
                f'Included: {count_images} images, {count_posts} posts, {count_pages} pages.')

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Error generating sitemap: {str(e)}'))
