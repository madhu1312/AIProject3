/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = new Collection({
    "id": "articles",
    "name": "articles",
    "type": "base",
    "system": false,
    "schema": [
      {
        "id": "title_field",
        "name": "title",
        "type": "text",
        "system": false,
        "required": true,
        "options": {
          "min": 1,
          "max": 500,
          "pattern": ""
        }
      },
      {
        "id": "content_field",
        "name": "content",
        "type": "text",
        "system": false,
        "required": false,
        "options": {
          "min": null,
          "max": null,
          "pattern": ""
        }
      },
      {
        "id": "excerpt_field",
        "name": "excerpt",
        "type": "text",
        "system": false,
        "required": false,
        "options": {
          "min": null,
          "max": 1000,
          "pattern": ""
        }
      },
      {
        "id": "status_field",
        "name": "status",
        "type": "select",
        "system": false,
        "required": true,
        "options": {
          "maxSelect": 1,
          "values": ["draft", "published", "archived"]
        }
      },
      {
        "id": "author_field",
        "name": "author",
        "type": "text",
        "system": false,
        "required": false,
        "options": {
          "min": null,
          "max": 200,
          "pattern": ""
        }
      },
      {
        "id": "slug_field",
        "name": "slug",
        "type": "text",
        "system": false,
        "required": true,
        "options": {
          "min": 1,
          "max": 500,
          "pattern": ""
        }
      },
      {
        "id": "published_field",
        "name": "published",
        "type": "date",
        "system": false,
        "required": false,
        "options": {
          "min": "",
          "max": ""
        }
      },
      {
        "id": "tags_field",
        "name": "tags",
        "type": "json",
        "system": false,
        "required": false,
        "options": {}
      }
    ],
    "indexes": [],
    "listRule": "",
    "viewRule": "",
    "createRule": "",
    "updateRule": "",
    "deleteRule": "",
    "options": {}
  });

  return app.save(collection);
}, (app) => {
  const collection = app.findCollectionByNameOrId("articles");
  return app.delete(collection);
});
