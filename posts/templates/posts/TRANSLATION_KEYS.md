# Translation Keys for Posts Templates

## Common Keys

### Site
- `articles.site_name` - Site name (Mon Blog Django)

### Articles (article_detail.html)
- `articles.by` - "By" (author prefix)
- `articles.your_reaction` - "Your reaction"
- `articles.login_to_react` - "Log in to react to this article"
- `articles.login` - "Log in"
- `articles.comments` - "Comments"
- `articles.leave_comment` - "Leave a comment"
- `articles.your_name` - "Your name"
- `articles.your_comment` - "Your comment"
- `articles.publish_comment` - "Publish comment"
- `articles.no_comments_yet` - "No comments yet"
- `articles.be_first_to_comment` - "Be the first to share your opinion on this article!"
- `articles.back_to_articles` - "Back to articles"

### Article Form (ajouter_article.html)
- `articles.add_title` - "Add Article"
- `articles.edit_title` - "Edit Article"
- `articles.create_new_article` - "Create a new article"
- `articles.edit_article` - "Edit article"
- `articles.update_your_content` - "Update your content"
- `articles.share_your_ideas` - "Share your ideas with the world"
- `articles.write_article` - "Write an article"
- `articles.edit_form_subtitle` - "Edit your article information"
- `articles.create_form_subtitle` - "Fill out the form below to publish your article"
- `articles.form_errors` - "Form errors"
- `articles.article_title` - "Article title"
- `articles.title_placeholder` - "A catchy title for your article..."
- `articles.article_summary` - "Article summary"
- `articles.summary_placeholder` - "Catchy summary of your article (300 characters max)..."
- `articles.summary_help_text` - "This summary will appear on the homepage to entice readers to read the full article."
- `articles.article_content` - "Article content"
- `articles.content_placeholder` - "Write your article here... Share your ideas, experiences, knowledge..."
- `articles.content_help_text` - "Tip: Structure your article with clear and concise paragraphs."
- `articles.categories` - "Categories"
- `articles.no_categories` - "No categories available."
- `articles.create_one` - "Create one"
- `articles.categories_help_text` - "Select one or more categories to classify your article."
- `articles.article_image` - "Article image"
- `articles.optional` - "optional"
- `articles.click_to_upload` - "Click to upload"
- `articles.or_drag_drop` - "or drag and drop"
- `articles.image_formats` - "PNG, JPG or JPEG (MAX. 5MB)"
- `articles.change` - "Change"
- `articles.delete` - "Delete"
- `articles.image_selected` - "Image selected"
- `articles.image_help_text` - "A nice image will make your article more attractive!"
- `articles.cancel` - "Cancel"
- `articles.save_as_draft` - "Save as draft"
- `articles.publish_article` - "Publish article"
- `articles.update_article` - "Update article"
- `articles.tips_title` - "Tips for a good article"
- `articles.tip_catchy_title` - "Choose a catchy and descriptive title"
- `articles.tip_structure_content` - "Structure your content with short paragraphs"
- `articles.tip_proofread` - "Proofread before publishing"

### Explorer (explorer.html)
- `articles.explore_title` - "Explorer"
- `articles.explore_subtitle` - "Discover all our articles"
- `articles.explore_banner_title` - "Discover our complete library"
- `articles.explore_banner_subtitle` - "Explore all our articles, find hidden gems and dive into content that interests you."
- `articles.explore_banner_info` - "Articles for all tastes • Filter according to your preferences"
- `articles.search_placeholder` - "Search in articles..."
- `articles.all_categories` - "All categories"
- `articles.search` - "Search"
- `articles.clear` - "Clear"
- `articles.articles_in_category` - "Articles in category"
- `articles.all_articles` - "All articles"
- `articles.browse_collection` - "Browse our entire collection of articles"
- `articles.verified_author` - "Verified author"
- `articles.like` - "Like"
- `articles.love` - "Love"
- `articles.laugh` - "Funny"
- `articles.wow` - "Wow"
- `articles.sad` - "Sad"
- `articles.angry` - "Angry"
- `articles.more` - "More"
- `articles.all_reactions` - "All reactions"
- `articles.new` - "New"
- `articles.multiple_reactions_info` - "You can now add multiple reactions! Click again to remove."
- `articles.view_full_article` - "View full article"
- `articles.read_time` - "5 min"
- `articles.read` - "Read"
- `articles.your_story_starts_here` - "Your story starts here"
- `articles.be_first_to_share` - "Be the first to share your ideas and inspire others with your first article."
- `articles.write_first_article` - "Write my first article"
- `articles.login_to_write` - "Log in to write"
- `articles.login_required_to_react` - "You must be logged in to react to articles"

### Categories (categories.html & category_detail.html)
- `categories.title` - "Categories"
- `categories.site_name` - "My Django Blog"
- `categories.subtitle` - "Explore articles by theme"
- `categories.explore` - "Explore"
- `categories.no_categories_yet` - "No categories yet"
- `categories.categories_will_be_created` - "Categories will be created automatically when articles are published."
- `categories.create_category` - "Create a category"
- `categories.articles_in_category` - "Articles in this category"
- `categories.all_categories` - "All categories"
- `categories.no_articles_in_category` - "No articles in this category"
- `categories.write_article` - "Write an article"
- `categories.login_to_write` - "Log in to write"

## Pluralization Examples

### Using blocktrans with count
```django
{% blocktrans count count=value %}
{{ count }} word
{% plural %}
{{ count }} words
{% endblocktrans %}
```

### Examples in templates:
- Word count
- Comment count
- Reaction count
- Article count
- Search results

## Notes

1. All text strings have been replaced with translation tags
2. Keys are organized hierarchically (articles.*, categories.*)
3. Placeholders use single quotes in template tags
4. blocktrans is used for strings with variables and pluralization
5. trans is used for simple strings without variables