import os
try:
    import simplejson as json
except ImportError:
    import json
from DateTime import DateTime

from Products.naayaUpdater.updates import UpdateScript
from naaya.core.zope2util import path_in_site


class ExportContent(UpdateScript):
    title = ('Export content to JSON, files to disk')
    authors = ['Valentin Dumitru']
    creation_date = 'Aug 5, 2016'

    def _update(self, portal):
        # schema_tool = portal.getSchemaTool()
        # meta_types = schema_tool.listSchemas().keys()
        process_export = {'Naaya News': self.export_news,
                          'Naaya Event': self.export_events}
        for ob in portal.getCatalogedObjectsA(meta_type=process_export.keys()):
            url = path_in_site(ob)
            portal_id = portal.getId()
            ob_data = format_DateTime(dict(ob.__dict__))
            ob_data['url'] = url

            ob_data = process_export[ob.meta_type](ob, ob_data, portal_id)

            data_filename = os.path.join(ob_data['folder'], ob.getId()+'.json')
            with open(data_filename, 'wb') as f:
                f.write(json.dumps(ob_data))
                self.log.info(
                    'Exported %s %s' % (ob.meta_type, ob.absolute_url()))
        return True

    def export_common(self, ob, ob_data, folder):
        if ob_data.get('__annotations__'):
            del(ob_data['__annotations__'])
        if ob_data.get('version'):
            # it means the object has been checked out by an user
            # but likely forgotten in this state. not relevant for export
            del(ob_data['version'])
        ob_data = self.process_comments(ob, ob_data, folder)
        ob_data['folder'] = folder
        return ob_data

    def export_news(self, ob, ob_data, portal_id):
        folder = os.path.join('content_export', portal_id, 'news',
                              ob_data['url'])
        if not os.path.exists(folder):
            os.makedirs(folder)
        for pic_id in ['bigpicture', 'smallpicture']:
            if getattr(ob, pic_id, None):
                filename = os.path.join(folder, pic_id+'.jpg')
                with open(filename, 'wb') as f:
                    f.write(getattr(ob, pic_id))
                    self.log.info('Exported %s for News item %s' % (
                        pic_id, ob.getId()))
                del(ob_data[pic_id])
        return self.export_common(ob, ob_data, folder)

    def export_events(self, ob, ob_data, portal_id):
        folder = os.path.join('content_export', portal_id, 'events',
                              ob_data['url'])
        if not os.path.exists(folder):
            os.makedirs(folder)
        return self.export_common(ob, ob_data, folder)

    def process_comments(self, ob, ob_data, folder):
        if ob_data.get('.comments'):
            # remove the comments from ob_data and export them from
            # the ob itself
            del(ob_data['.comments'])
            for comment in getattr(ob, '.comments').objectValues(
                    'Naaya Comment'):
                comment_id = comment.getId()
                comment_filename = os.path.join(
                    folder, 'comment_'+comment_id+'.json')
                with open(comment_filename, 'wb') as f:
                    f.write(json.dumps(format_DateTime(comment.__dict__)))
                    self.log.info(
                        'Exported comment %s for News item %s' % (
                            comment_id, ob.getId()))
        if ob_data.get('_NyComments__comments_collection'):
            # remove the comments from ob_data and export them from
            # the ob itself
            del(ob_data['_NyComments__comments_collection'])
            for comment_id, comment in getattr(
                    ob, '_NyComments__comments_collection').items():
                comment_filename = os.path.join(
                    folder, 'comment_'+comment_id+'.json')
                comment_data = format_DateTime(comment.__dict__)
                with open(comment_filename, 'wb') as f:
                    f.write(json.dumps(comment_data))
                    self.log.info(
                        'Exported comment %s for News item %s' % (
                            comment_id, ob.getId()))
        return ob_data


def format_DateTime(dictionary):
    for k, v in dictionary.items():
        if isinstance(v, DateTime):
            dictionary[k] = v.strftime('%Y-%m-%dT%H:%M:%S')
    return dictionary
