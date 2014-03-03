import argparse
from pennyweb.manage import manager
from pennyweb.models import freshbooks


@manager.option('-c', '--client', default=None,
                help="Limit to a single client")
@manager.option('-y', '--yes', default=False, action='store_true',
                help="Actually push the changes")
def tendollar(client, yes):
    c = freshbooks.get_client()
    for recurring in get_all_recurring(c, client):
        print recurring.client_id, recurring.first_name, recurring.last_name
        for line in recurring.lines.line:
            print '  {:>5} {:8} {:6.2f} {}'.format(
                line.line_id, line.name, line.amount.pyval, line.description)

        if yes:
            c.recurring.update(recurring=dict(
                recurring_id=recurring.recurring_id,
                lines=add_tendollar_lines(recurring.lines.line)
            ))


def get_all_recurring(c, client=None, folder='active'):
    page = 0
    last_page = 1
    while page < last_page:
        page += 1
        if client:
            res = c.recurring.list(folder=folder, page=page, client_id=client)
        else:
            res = c.recurring.list(folder=folder, page=page)
        last_page = int(res.recurrings.attrib['pages'])

        for recurring in res.recurrings.recurring:
            yield recurring


def add_tendollar_lines(lines):
    new_lines = []
    for line in lines:
        # Skip existing TENDOLLAR items
        if line.name == 'TENDOLLAR':
            continue

        new_lines.append(freshbooks.api.types.line(
            name=line.name,
            unit_cost=line.unit_cost,
            quantity=line.quantity,
            description=line.description
        ))
        if line.name in ('ATXDUES', 'FAMILY30'):
            new_lines.append(freshbooks.api.types.line(
                name='TENDOLLAR',
                unit_cost='10',
                quantity='1',
                description=(
                    "$10 dues increase for month of ::month::"
                    if line.name == 'ATXDUES'
                    else "$10 dues increase for " + line.description
                )
            ))
    return new_lines

if __name__ == '__main__':
    manager.run()
