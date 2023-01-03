from forms import LinkForm


def modify_links(links, total_no_rows):
    new_links = links
    empty_link_form = LinkForm()
    empty_link_form.url = ""
    empty_link_form.label = ""
    for _ in range(len(links), total_no_rows):
        new_links.append(empty_link_form)
    return new_links
