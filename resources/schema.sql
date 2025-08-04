CREATE TABLE log (
  id       BIGINT UNSIGNED   AUTO_INCREMENT,
  time     TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP,
  src_ip   VARCHAR(39)       NOT NULL,
  src_port SMALLINT UNSIGNED NOT NULL,
  dst_ip   VARCHAR(39)       NOT NULL,
  dst_port SMALLINT UNSIGNED NOT NULL,
  protocol VARCHAR(255)      NULL DEFAULT NULL,

  PRIMARY KEY (id),

  INDEX idx_time (time),
  INDEX idx_protocol (protocol)
);

-- protocol 필드는 Nullable, 기본값 NULL을 명시
