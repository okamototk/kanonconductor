UPDATE enum SET name = '対応済' WHERE type ='resolution' AND value = '1';
UPDATE enum SET name = '不正' WHERE type ='resolution' AND value = '2';
UPDATE enum SET name = '対応しない' WHERE type ='resolution' AND value = '3';
UPDATE enum SET name = '重複' WHERE type ='resolution' AND value = '4';
UPDATE enum SET name = '再現しない' WHERE type ='resolution' AND value = '5';
UPDATE enum SET name = '今すぐ' WHERE type ='priority' AND value = '1';
UPDATE enum SET name = '急いで' WHERE type ='priority' AND value = '2';
UPDATE enum SET name = '高め' WHERE type ='priority' AND value = '3';
UPDATE enum SET name = '通常' WHERE type ='priority' AND value = '4';
UPDATE enum SET name = '低め' WHERE type ='priority' AND value = '5';
UPDATE enum SET name = 'バグ' WHERE type ='ticket_type' AND value = '1';
UPDATE enum SET name = '機能追加' WHERE type ='ticket_type' AND value = '2';
UPDATE enum SET name = '仕様変更' WHERE type ='ticket_type' AND value = '3';
UPDATE component SET name ='その他' WHERE name = 'component1';
UPDATE component SET name ='ユーザ管理機能' WHERE name = 'component2';
INSERT INTO component VALUES('検索機能', 'somebody', '');
UPDATE milestone SET name ='要件定義完了', description='要件定義の完了' WHERE name = 'milestone1';
UPDATE milestone SET name ='1.0αリリース', description='お客様の要件確認用のプロトタイプリリース。[[BR]][[QueryChart(query:?type=タスク,col:due_close,width:800)]]' WHERE name = 'milestone2';
UPDATE milestone SET name ='1.0βリリース', description='機能試験終了後のお客様受け入れ試験用のリリース' WHERE name = 'milestone3';
UPDATE milestone SET name ='1.0リリース', description='正式版リリース' WHERE name = 'milestone4';
UPDATE version SET name ='1.0α' WHERE name = '1.0';
UPDATE version SET name ='1.0β' WHERE name = '2.0';

INSERT INTO enum VALUES('ticket_type', 'タスク', '4');
INSERT INTO enum VALUES('ticket_type', '課題', '5');
INSERT INTO enum VALUES('ticket_type', '連絡', '6');

INSERT INTO session_attribute values ('admin', '1','name','管理太郎');
INSERT INTO session_attribute values ('admin', '1','enabled','1');
INSERT INTO session_attribute values ('guest', '1','name','客人開発者');
INSERT INTO session_attribute values ('guest', '1','enabled','1');
INSERT INTO session_attribute values ('leader', '1','name','頭春蔵');
INSERT INTO session_attribute values ('leader', '1','enabled','1');
INSERT INTO attachment values ('wiki', 'UserManagerPluginPictures', 'admin-penguin.png',0,0,'admin', 'Avatar','127.0.0.1');
INSERT INTO attachment values ('wiki', 'UserManagerPluginPictures', 'guest-hamster.png',0,0,'guest', 'Avatar','127.0.0.1');
INSERT INTO attachment values ('wiki', 'UserManagerPluginPictures', 'leader-cat.png',0,0,'leader', 'Avatar','127.0.0.1');

INSERT INTO report VALUES('9','','未解決チケット(進捗確認用)',

"SELECT owner AS __group__,
   id AS ticket,
   summary as '概要　　　　',
   a.value as '開始日',
   c.value as '終了日',
   (CASE status WHEN 'assigned' THEN d.value||' *' ELSE d.value END) AS '達成率',
   t.type AS 'タイプ　', 
   t.priority as '優先度',
   changetime AS _changetime, description AS _description,
   reporter AS _reporter,
   (CASE  WHEN c.value ='' THEN 5
          WHEN c.value < strftime('%Y/%m/%d','now') THEN 1
          WHEN c.value < strftime('%Y/%m/%d','now', '7 day') THEN 2
          ELSE 3 END) AS __color__
  FROM ticket t
  LEFT JOIN enum p ON p.name = t.priority AND p.type = 'priority'
  LEFT JOIN ticket_custom a ON a.ticket = t.id AND a.name = 'due_assign' 
  LEFT JOIN ticket_custom c ON c.ticket = t.id AND c.name = 'due_close' 
  LEFT JOIN ticket_custom d ON d.ticket = t.id AND d.name = 'complete'
  WHERE status IN ('new', 'assigned', 'reopened') 
  ORDER BY owner, a.value, p.value, milestone, t.type, time","
 * 担当者別に未解決チケットを表示します。
 * 終了日順に表示し、終了日を過ぎたものは、赤で、終了日が1週間以内のものは黄色で表示します。
 * チケットに着手済みであれば、達成率に '*' が付与されます。
 * 終了日が設定されていないものについては、青で表示します。
");
